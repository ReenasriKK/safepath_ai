import os
from flask import Flask
from flask_login import LoginManager
from models import db, User, Hazard
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safepath-ai-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and seed hazards
def init_db():
    with app.app_context():
        db.create_all()

        # Add new DetectionHistory columns if missing
        try:
            result = db.session.execute(text("PRAGMA table_info('detection_history')")).fetchall()
            existing_columns = {row[1] for row in result}
            if 'safety_level' not in existing_columns:
                db.session.execute(text('ALTER TABLE detection_history ADD COLUMN safety_level VARCHAR(64)'))
            if 'primary_hazard' not in existing_columns:
                db.session.execute(text('ALTER TABLE detection_history ADD COLUMN primary_hazard VARCHAR(128)'))
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Seed initial hazards if they don't exist
        hazards_data = [
            ('Pothole', 20),
            ('Flooded Road', 30),
            ('Road Block', 25),
            ('Garbage', 5),
            ('Fallen Tree', 25),
            ('Construction Area', 15),
            ('Low Visibility', 20),
            ('Damaged Road', 15)
        ]

        for name, score in hazards_data:
            if not Hazard.query.filter_by(hazard_type=name).first():
                hazard = Hazard(hazard_type=name, base_risk_score=score)
                db.session.add(hazard)

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@safepath.ai',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)

        db.session.commit()

# Import and register blueprints (to be created in next steps)
from routes import auth_bp, main_bp, ai_bp
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(ai_bp)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
