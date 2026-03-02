"""
Faculty Service
Business logic for faculty authentication and management (MongoDB)
"""
from datetime import datetime, timedelta
from src.models import get_db, faculty_to_dict, obj_id
import secrets
import random


class FacultyService:
    """Service class for faculty operations using MongoDB"""

    @staticmethod
    def generate_otp(email, name=None):
        """Generate OTP for faculty login"""
        try:
            db = get_db()
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            faculty = db.faculty.find_one({'email': email})

            if not faculty:
                if not name:
                    return False, "Name is required for new faculty"
                db.faculty.insert_one({
                    'name': name,
                    'email': email,
                    'sections': '',
                    'otp': otp,
                    'otp_created_at': datetime.utcnow(),
                    'remember_token': None,
                    'remember_expires': None,
                    'created_at': datetime.utcnow(),
                })
            else:
                db.faculty.update_one(
                    {'email': email},
                    {'$set': {'otp': otp, 'otp_created_at': datetime.utcnow()}}
                )

            print(f"📧 OTP for {email}: {otp}")
            return True, otp

        except Exception as e:
            return False, str(e)

    @staticmethod
    def verify_otp(email, otp, remember_me=False):
        """Verify OTP and optionally create remember token"""
        try:
            db = get_db()
            faculty = db.faculty.find_one({'email': email})

            if not faculty:
                return False, "Faculty not found"
            if not faculty.get('otp'):
                return False, "No OTP generated. Please request a new one"

            # Check expiry (10 minutes)
            if faculty.get('otp_created_at'):
                age = datetime.utcnow() - faculty['otp_created_at']
                if age > timedelta(minutes=10):
                    return False, "OTP expired. Please request a new one"

            if faculty['otp'] != otp:
                return False, "Invalid OTP"

            updates = {'otp': None, 'otp_created_at': None}
            token = None

            if remember_me:
                token = secrets.token_urlsafe(32)
                updates['remember_token'] = token
                updates['remember_expires'] = datetime.utcnow() + timedelta(days=30)

            db.faculty.update_one({'email': email}, {'$set': updates})

            # Return updated faculty dict
            faculty.update(updates)
            return True, (faculty_to_dict(faculty), token)

        except Exception as e:
            return False, str(e)

    @staticmethod
    def verify_remember_token(email, token):
        """Verify remember me token"""
        try:
            db = get_db()
            faculty = db.faculty.find_one({'email': email})

            if not faculty:
                return False, "Faculty not found"
            if not faculty.get('remember_token') or faculty['remember_token'] != token:
                return False, "Invalid token"
            if faculty.get('remember_expires') and faculty['remember_expires'] < datetime.utcnow():
                return False, "Token expired. Please login again"

            return True, faculty_to_dict(faculty)

        except Exception as e:
            return False, str(e)

    @staticmethod
    def logout(email):
        """Logout faculty and clear remember token"""
        try:
            db = get_db()
            db.faculty.update_one(
                {'email': email},
                {'$set': {'remember_token': None, 'remember_expires': None}}
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_faculty_by_email(email):
        """Get faculty by email"""
        db = get_db()
        doc = db.faculty.find_one({'email': email})
        return faculty_to_dict(doc)

    @staticmethod
    def update_sections(email, sections):
        """Update faculty sections"""
        try:
            db = get_db()
            faculty = db.faculty.find_one({'email': email})
            if not faculty:
                return False, "Faculty not found"

            if isinstance(sections, list):
                sections = ','.join(sections)

            db.faculty.update_one({'email': email}, {'$set': {'sections': sections}})
            faculty['sections'] = sections
            return True, faculty_to_dict(faculty)

        except Exception as e:
            return False, str(e)
