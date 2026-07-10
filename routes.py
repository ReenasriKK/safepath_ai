from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Trip, Report, Hazard, DetectionHistory, EmergencyContact
import os
import uuid
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
ai_bp = Blueprint('ai', __name__)

# --- Auth Routes ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))

# --- Main Routes ---
@main_bp.route('/')
def landing():
    return render_template('landing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    trips_count = Trip.query.filter_by(user_id=current_user.id).count()
    hazards_count = DetectionHistory.query.filter_by(user_id=current_user.id).count()
    reports_count = Report.query.filter_by(user_id=current_user.id).count()
    
    recent_detections = DetectionHistory.query.filter_by(user_id=current_user.id).order_by(DetectionHistory.timestamp.desc()).limit(5).all()
    
    # Calculate average safety score
    trips = Trip.query.filter_by(user_id=current_user.id).all()
    avg_safety = sum([t.safety_score for t in trips]) / len(trips) if trips else 0

    # Prepare analytics data: hazard category counts and weekly detections
    from collections import Counter
    import json
    labels = []
    counts = []

    all_detections = DetectionHistory.query.filter_by(user_id=current_user.id).all()
    counter = Counter()
    for d in all_detections:
        objs = d.get_objects()
        for o in objs:
            lbl = o.get('label') if isinstance(o, dict) else None
            if lbl:
                counter[lbl] += 1

    if counter:
        labels = list(counter.keys())
        counts = [counter[l] for l in labels]

    # Weekly data (last 7 days)
    from datetime import timedelta
    today = datetime.utcnow().date()
    week_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    week_labels = [d.strftime('%a') for d in week_days]
    week_counts = []
    for wd in week_days:
        c = DetectionHistory.query.filter(
            DetectionHistory.user_id == current_user.id,
            db.func.date(DetectionHistory.timestamp) == wd
        ).count()
        week_counts.append(c)

    # AI status (whether detection modules available)
    try:
        import importlib
        ultralytics_spec = importlib.util.find_spec('ultralytics')
        ai_status = 'Online' if ultralytics_spec else 'Unavailable'
    except Exception:
        ai_status = 'Unavailable'

    return render_template('dashboard.html', 
                           trips_count=trips_count, 
                           hazards_count=hazards_count, 
                           reports_count=reports_count,
                           avg_safety=round(avg_safety, 2),
                           recent_detections=recent_detections,
                           hazard_labels_json=json.dumps(labels),
                           hazard_counts_json=json.dumps(counts),
                           week_labels_json=json.dumps(week_labels),
                           week_counts_json=json.dumps(week_counts),
                           ai_status=ai_status)

@main_bp.route('/map')
@login_required
def map_page():
    reports = Report.query.filter(Report.location_lat.isnot(None), Report.location_lng.isnot(None)).order_by(Report.timestamp.desc()).all()
    return render_template('map.html', reports=reports)

@main_bp.route('/emergency', methods=['GET', 'POST'])
@login_required
def emergency():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        flash('Emergency alert sent to your saved contacts. Stay safe.')
        return redirect(url_for('main.emergency'))
    return render_template('emergency.html', contacts=contacts)


@main_bp.route('/route-compare', methods=['GET', 'POST'])
@login_required
def route_compare():
    from route_utils import generate_routes
    from safety_engine import compute_total_risk, risk_to_safety_score, generate_ai_recommendation

    suggested = []
    recommended = None
    source = ''
    destination = ''
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        routes = generate_routes(source or 'A', destination or 'B', count=3)
        best_score = -1
        for r in routes:
            computed_risk = compute_total_risk(r.get('hazards', []))
            safety_score = risk_to_safety_score(computed_risk, max_risk=100)
            r['risk'] = computed_risk
            r['safety_score'] = safety_score
            r['safety_level'] = 'Safe' if safety_score>=80 else ('Moderate' if safety_score>=50 else 'Dangerous')
            r['ai_reco'] = generate_ai_recommendation(r.get('hazards', []), computed_risk, safety_score)
            if safety_score > best_score:
                best_score = safety_score
                recommended = r['name']
        suggested = routes

    return render_template('route_compare.html', suggested=suggested, recommended=recommended, source=source, destination=destination)

@main_bp.route('/history')
@login_required
def history():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.timestamp.desc()).all()
    hazard_records = DetectionHistory.query.filter_by(user_id=current_user.id).order_by(DetectionHistory.timestamp.desc()).all()
    return render_template('history.html', trips=trips, hazard_records=hazard_records)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        # Handle profile update or emergency contact addition
        action = request.form.get('action')
        if action == 'add_contact':
            name = request.form.get('name')
            phone = request.form.get('phone')
            rel = request.form.get('relationship')
            new_contact = EmergencyContact(user_id=current_user.id, name=name, phone=phone, relationship=rel)
            db.session.add(new_contact)
            db.session.commit()
            flash('Emergency contact added')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', contacts=contacts)

@main_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    all_reports = Report.query.all()
    return render_template('admin.html', users=users, reports=all_reports)

# --- AI & Detection Routes ---
@ai_bp.route('/hazard-detection', methods=['GET', 'POST'])
@login_required
def hazard_detection():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(input_path)
            
            output_filename = f"detected_{unique_filename}"
            # Import detector lazily to avoid heavy imports at app startup
            try:
                from ai.detect import run_detection
                from safety_engine import compute_total_risk, risk_to_safety_score, generate_ai_report

                detections, risk_score, recommendation, output_path = run_detection(input_path, output_filename)

                # Recompute and normalize risk using the Safety Score Engine
                computed_risk = compute_total_risk(detections)
                safety_score = risk_to_safety_score(computed_risk, max_risk=100)
                ai_report = generate_ai_report(detections, computed_risk, safety_score)

                # Prefer computed values for storage and display
                risk_score = computed_risk
                recommendation = ai_report['summary']
                safety_level = ai_report['level']
                suggested_action = ai_report['action']
                alternative_recommendation = ai_report['alternative']
                ai_explanation = ai_report['summary']
                report_hazard_text = ai_report['hazard_text']
            except Exception as e:
                # If AI dependencies aren't installed or detection fails, show a friendly message
                current_app.logger.exception('Detection failed')
                flash('Hazard detection is currently unavailable (missing AI dependencies).')
                return redirect(request.url)
            
            # Save to history
            history = DetectionHistory(
                user_id=current_user.id,
                image_path=unique_filename,
                detected_image_path=output_filename,
                risk_score=risk_score,
                safety_level=safety_level,
                safety_recommendation=recommendation,
                primary_hazard=report_hazard_text or 'No hazards detected'
            )
            history.set_objects(detections)
            db.session.add(history)
            db.session.commit()
            
            return render_template('hazard_result.html', 
                                   original=unique_filename, 
                                   detected=output_filename, 
                                   detections=detections,
                                   risk_score=risk_score,
                                   recommendation=recommendation,
                                   safety_level=safety_level,
                                   suggested_action=suggested_action,
                                   alternative_recommendation=alternative_recommendation,
                                   ai_explanation=ai_explanation,
                                   report_hazard_text=report_hazard_text)
            
    return render_template('hazard_detection.html')

@main_bp.route('/community-reports', methods=['GET', 'POST'])
@login_required
def community_reports():
    if request.method == 'POST':
        desc = request.form.get('description')
        cat = request.form.get('category')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        
        file = request.files.get('photo')
        photo_path = None
        if file:
            filename = secure_filename(file.filename)
            unique_filename = f"report_{uuid.uuid4()}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            photo_path = unique_filename
            
        report = Report(
            user_id=current_user.id,
            description=desc,
            category=cat,
            location_lat=float(lat) if lat else None,
            location_lng=float(lng) if lng else None,
            photo_path=photo_path
        )
        db.session.add(report)
        db.session.commit()
        flash('Report submitted successfully')
        return redirect(url_for('main.community_reports'))
        
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    report_stats = {
        'total': len(reports),
        'verified': sum(1 for r in reports if r.status == 'verified'),
        'resolved': sum(1 for r in reports if r.status == 'resolved'),
        'pending': sum(1 for r in reports if r.status == 'pending'),
    }
    category_counts = {}
    for r in reports:
        category = r.category or 'Other'
        category_counts[category] = category_counts.get(category, 0) + 1

    return render_template('community_reports.html', reports=reports, report_stats=report_stats, category_counts=category_counts)

# API for map routing
@main_bp.route('/api/save-trip', methods=['POST'])
@login_required
def save_trip():
    data = request.json
    new_trip = Trip(
        user_id=current_user.id,
        source=data.get('source'),
        destination=data.get('destination'),
        route_data=data.get('route_data'),
        safety_score=data.get('safety_score', 100.0)
    )
    db.session.add(new_trip)
    db.session.commit()
    return jsonify({'status': 'success', 'trip_id': new_trip.id})

# Serve uploaded files
from flask import send_from_directory

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
