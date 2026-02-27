"""
NFC Tag Management Service
Business logic for NFC tag operations
"""
from src.models import db, Student
from src.utils.validators import validate_nfc_tag
from sqlalchemy.exc import IntegrityError


class NFCService:
    """Service class for NFC tag management"""
    
    @staticmethod
    def register_tag(student_id, nfc_tag_id):
        """
        Register an NFC tag to a student
        
        Args:
            student_id: ID of the student
            nfc_tag_id: NFC tag identifier
            
        Returns:
            tuple: (success, message_or_student)
        """
        # Validate tag ID
        is_valid, error = validate_nfc_tag(nfc_tag_id)
        if not is_valid:
            return False, error
        
        try:
            # Get student
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            # Check if tag is already registered to another student
            existing = Student.query.filter_by(nfc_tag_id=nfc_tag_id.strip()).first()
            if existing and existing.id != student_id:
                return False, f"NFC tag already registered to {existing.name} ({existing.register_number})"
            
            # Register tag
            student.nfc_tag_id = nfc_tag_id.strip()
            db.session.commit()
            
            return True, student
            
        except IntegrityError:
            db.session.rollback()
            return False, "NFC tag already registered to another student"
        except Exception as e:
            db.session.rollback()
            return False, f"Error registering NFC tag: {str(e)}"
    
    @staticmethod
    def unregister_tag(student_id):
        """
        Remove NFC tag from a student
        
        Args:
            student_id: ID of the student
            
        Returns:
            tuple: (success, message)
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            if not student.nfc_tag_id:
                return False, "Student does not have an NFC tag registered"
            
            student.nfc_tag_id = None
            db.session.commit()
            
            return True, "NFC tag unregistered successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error unregistering NFC tag: {str(e)}"
    
    @staticmethod
    def get_student_by_tag(nfc_tag_id):
        """
        Get student associated with an NFC tag
        
        Args:
            nfc_tag_id: NFC tag identifier
            
        Returns:
            Student object or None
        """
        return Student.query.filter_by(nfc_tag_id=nfc_tag_id.strip()).first()
    
    @staticmethod
    def is_tag_registered(nfc_tag_id):
        """
        Check if an NFC tag is already registered
        
        Args:
            nfc_tag_id: NFC tag identifier
            
        Returns:
            bool: True if registered, False otherwise
        """
        return Student.query.filter_by(nfc_tag_id=nfc_tag_id.strip()).first() is not None
