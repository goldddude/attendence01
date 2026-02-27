"""
Database Models for NFC Attendance System
Uses SQLAlchemy ORM for database abstraction
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    """Student model with NFC tag support"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    section = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(20), nullable=False)  # e.g., "Year 1", "2021-2025"
    nfc_tag_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert student object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'register_number': self.register_number,
            'section': self.section,
            'department': self.department,
            'duration': self.duration,
            'nfc_tag_id': self.nfc_tag_id,
            'has_nfc': self.nfc_tag_id is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Student {self.register_number}: {self.name}>'


class Faculty(db.Model):
    """Faculty model for login and authentication"""
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    sections = db.Column(db.String(500), nullable=True)  # Comma-separated sections like "S-01,S-02"
    otp = db.Column(db.String(6), nullable=True)  # Current OTP
    otp_created_at = db.Column(db.DateTime, nullable=True)
    remember_token = db.Column(db.String(100), nullable=True, unique=True)
    remember_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert faculty object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'sections': self.sections.split(',') if self.sections else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Faculty {self.email}: {self.name}>'


class Attendance(db.Model):
    """Attendance record model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    recorded_by = db.Column(db.String(100), nullable=False)  # Faculty name
    section = db.Column(db.String(20), nullable=True, index=True)  # Section like S-01, S-02
    subject = db.Column(db.String(100), nullable=True, index=True)  # Subject name
    date = db.Column(db.String(20), nullable=True, index=True)  # Date of class (YYYY-MM-DD)
    class_time = db.Column(db.String(20), nullable=True)  # Class time slot (e.g., 09:00-09:50)
    
    def to_dict(self):
        """Convert attendance object to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'register_number': self.student.register_number if self.student else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'recorded_by': self.recorded_by,
            'section': self.section,
            'subject': self.subject,
            'date': self.date,
            'class_time': self.class_time
        }
    
    def __repr__(self):
        return f'<Attendance {self.student_id} at {self.timestamp}>'
