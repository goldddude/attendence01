"""
NFC Tag Management Service
Business logic for NFC tag operations (MongoDB)
"""
from src.models import get_db, student_to_dict, obj_id
from src.utils.validators import validate_nfc_tag


class NFCService:
    """Service class for NFC tag management using MongoDB"""

    @staticmethod
    def register_tag(student_id, nfc_tag_id):
        """Register an NFC tag to a student"""
        is_valid, error = validate_nfc_tag(nfc_tag_id)
        if not is_valid:
            return False, error

        try:
            db = get_db()
            oid = obj_id(student_id)
            if not oid:
                return False, "Invalid student ID"

            student = db.students.find_one({'_id': oid})
            if not student:
                return False, "Student not found"

            tag = nfc_tag_id.strip()

            # Check if tag is already used by another student
            existing = db.students.find_one({'nfc_tag_id': tag})
            if existing and str(existing['_id']) != str(oid):
                return False, f"NFC tag already registered to {existing['name']} ({existing['register_number']})"

            from datetime import datetime
            db.students.update_one(
                {'_id': oid},
                {'$set': {'nfc_tag_id': tag, 'updated_at': datetime.utcnow()}}
            )
            student['nfc_tag_id'] = tag
            return True, student_to_dict(student)

        except Exception as e:
            return False, f"Error registering NFC tag: {str(e)}"

    @staticmethod
    def unregister_tag(student_id):
        """Remove NFC tag from a student"""
        try:
            db = get_db()
            oid = obj_id(student_id)
            if not oid:
                return False, "Invalid student ID"

            student = db.students.find_one({'_id': oid})
            if not student:
                return False, "Student not found"
            if not student.get('nfc_tag_id'):
                return False, "Student does not have an NFC tag registered"

            from datetime import datetime
            db.students.update_one(
                {'_id': oid},
                {'$set': {'nfc_tag_id': None, 'updated_at': datetime.utcnow()}}
            )
            return True, "NFC tag unregistered successfully"

        except Exception as e:
            return False, f"Error unregistering NFC tag: {str(e)}"

    @staticmethod
    def get_student_by_tag(nfc_tag_id):
        """Get student associated with an NFC tag — returns raw doc"""
        db = get_db()
        return db.students.find_one({'nfc_tag_id': nfc_tag_id.strip()})

    @staticmethod
    def is_tag_registered(nfc_tag_id):
        """Check if an NFC tag is already registered"""
        db = get_db()
        return db.students.find_one({'nfc_tag_id': nfc_tag_id.strip()}) is not None
