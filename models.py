from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    profile_pic = db.Column(db.String(200), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trips = db.relationship('Trip', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    detections = db.relationship('DetectionHistory', backref='user', lazy=True)
    emergency_contacts = db.relationship('EmergencyContact', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    route_data = db.Column(db.Text)  # JSON string of coordinates
    safety_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_path = db.Column(db.String(200))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    risk_score = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, verified, resolved
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Hazard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hazard_type = db.Column(db.String(50), unique=True, nullable=False)
    base_risk_score = db.Column(db.Integer, nullable=False)

class DetectionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    detected_image_path = db.Column(db.String(200))
    detected_objects = db.Column(db.Text)  # JSON string of detected objects
    risk_score = db.Column(db.Integer)
    safety_level = db.Column(db.String(64))
    safety_recommendation = db.Column(db.String(256))
    primary_hazard = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def set_objects(self, objects_list):
        self.detected_objects = json.dumps(objects_list)

    def get_objects(self):
        return json.loads(self.detected_objects) if self.detected_objects else []

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    relationship = db.Column(db.String(50))
