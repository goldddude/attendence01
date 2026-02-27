"""
Faculty Service
Business logic for faculty authentication and management
"""
from src.models import db, Faculty
from datetime import datetime, timedelta
import secrets
import random


class FacultyService:
    """Service class for faculty operations"""
    
    @staticmethod
    def generate_otp(email, name=None):
        """Generate OTP for faculty login"""
        try:
            # Generate 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Find or create faculty
            faculty = Faculty.query.filter_by(email=email).first()
            
            if not faculty:
                if not name:
                    return False, "Name is required for new faculty"
                
                faculty = Faculty(
                    name=name,
                    email=email
                )
                db.session.add(faculty)
            
            # Update OTP
            faculty.otp = otp
            faculty.otp_created_at = datetime.utcnow()
            
            db.session.commit()
            
            # In production, send email here
            # For now, just return the OTP
            print(f"📧 OTP for {email}: {otp}")
            
            return True, otp
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def verify_otp(email, otp, remember_me=False):
        """Verify OTP and optionally create remember token"""
        try:
            faculty = Faculty.query.filter_by(email=email).first()
            
            if not faculty:
                return False, "Faculty not found"
            
            if not faculty.otp:
                return False, "No OTP generated. Please request a new one"
            
            # Check if OTP is expired (10 minutes)
            if faculty.otp_created_at:
                otp_age = datetime.utcnow() - faculty.otp_created_at
                if otp_age > timedelta(minutes=10):
                    return False, "OTP expired. Please request a new one"
            
            # Verify OTP
            if faculty.otp != otp:
                return False, "Invalid OTP"
            
            # Clear OTP
            faculty.otp = None
            faculty.otp_created_at = None
            
            # Generate remember token if requested
            token = None
            if remember_me:
                token = secrets.token_urlsafe(32)
                faculty.remember_token = token
                faculty.remember_expires = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            
            return True, (faculty, token)
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def verify_remember_token(email, token):
        """Verify remember me token"""
        try:
            faculty = Faculty.query.filter_by(email=email).first()
            
            if not faculty:
                return False, "Faculty not found"
            
            if not faculty.remember_token or faculty.remember_token != token:
                return False, "Invalid token"
            
            # Check if token is expired
            if faculty.remember_expires and faculty.remember_expires < datetime.utcnow():
                return False, "Token expired. Please login again"
            
            return True, faculty
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def logout(email):
        """Logout faculty and clear remember token"""
        try:
            faculty = Faculty.query.filter_by(email=email).first()
            
            if faculty:
                faculty.remember_token = None
                faculty.remember_expires = None
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_faculty_by_email(email):
        """Get faculty by email"""
        return Faculty.query.filter_by(email=email).first()
    
    @staticmethod
    def update_sections(email, sections):
        """Update faculty sections"""
        try:
            faculty = Faculty.query.filter_by(email=email).first()
            
            if not faculty:
                return False, "Faculty not found"
            
            # Convert list to comma-separated string
            if isinstance(sections, list):
                sections = ','.join(sections)
            
            faculty.sections = sections
            db.session.commit()
            
            return True, faculty
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
