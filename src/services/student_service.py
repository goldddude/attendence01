"""
Student Management Service
Business logic for student operations (MongoDB)
"""
from datetime import datetime
from bson import ObjectId
from src.models import get_db, student_to_dict, obj_id
from src.utils.validators import validate_student_data


class StudentService:
    """Service class for student management using MongoDB"""

    @staticmethod
    def create_student(data):
        """Create a new student"""
        is_valid, error = validate_student_data(data)
        if not is_valid:
            return False, error

        try:
            db = get_db()
            reg_num = data['register_number'].strip()

            # Check if register number already exists
            if db.students.find_one({'register_number': reg_num}):
                return False, f"Student with register number {reg_num} already exists"

            doc = {
                'name': data['name'].strip(),
                'register_number': reg_num,
                'section': data['section'].strip(),
                'department': data['department'].strip(),
                'duration': data['duration'].strip(),
                'nfc_tag_id': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }

            result = db.students.insert_one(doc)
            doc['_id'] = result.inserted_id
            return True, student_to_dict(doc)

        except Exception as e:
            return False, f"Error creating student: {str(e)}"

    @staticmethod
    def bulk_create_students(students_data):
        """Create multiple students from list"""
        success_count = 0
        failed_count = 0
        errors = []

        for idx, data in enumerate(students_data):
            success, result = StudentService.create_student(data)
            if success:
                success_count += 1
            else:
                failed_count += 1
                errors.append({
                    'row': idx + 2,
                    'register_number': data.get('register_number', 'N/A'),
                    'error': result
                })

        return success_count, failed_count, errors

    @staticmethod
    def get_student_by_id(student_id):
        """Get student by MongoDB _id — returns dict"""
        db = get_db()
        oid = obj_id(student_id)
        if not oid:
            return None
        doc = db.students.find_one({'_id': oid})
        return student_to_dict(doc)

    @staticmethod
    def get_student_doc_by_id(student_id):
        """Get raw MongoDB student document by _id"""
        db = get_db()
        oid = obj_id(student_id)
        if not oid:
            return None
        return db.students.find_one({'_id': oid})

    @staticmethod
    def get_student_by_register_number(register_number):
        """Get student by register number"""
        db = get_db()
        doc = db.students.find_one({'register_number': register_number})
        return student_to_dict(doc)

    @staticmethod
    def get_all_students(filters=None):
        """Get all students with optional filters"""
        db = get_db()
        query = {}

        if filters:
            if filters.get('section'):
                query['section'] = filters['section']
            if filters.get('department'):
                query['department'] = filters['department']
            if filters.get('duration'):
                query['duration'] = filters['duration']
            if 'has_nfc' in filters:
                if filters['has_nfc']:
                    query['nfc_tag_id'] = {'$ne': None, '$exists': True}
                else:
                    query['nfc_tag_id'] = None

        docs = db.students.find(query).sort('register_number', 1)
        return [student_to_dict(d) for d in docs]

    @staticmethod
    def search_students(search_term):
        """Search students by name or register number"""
        db = get_db()
        import re
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        docs = db.students.find({
            '$or': [
                {'name': {'$regex': pattern}},
                {'register_number': {'$regex': pattern}}
            ]
        }).sort('register_number', 1)
        return [student_to_dict(d) for d in docs]

    @staticmethod
    def delete_student(student_id):
        """Delete a student and their attendance records"""
        try:
            db = get_db()
            oid = obj_id(student_id)
            if not oid:
                return False, "Invalid student ID"

            if not db.students.find_one({'_id': oid}):
                return False, "Student not found"

            # Delete attendance records first
            db.attendance.delete_many({'student_id': oid})
            # Delete student
            db.students.delete_one({'_id': oid})

            return True, "Student deleted successfully"

        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
