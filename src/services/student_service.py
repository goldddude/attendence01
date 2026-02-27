"""
Student Management Service
Business logic for student operations
"""
from src.models import db, Student
from src.utils.validators import validate_student_data
from sqlalchemy.exc import IntegrityError


class StudentService:
    """Service class for student management"""
    
    @staticmethod
    def create_student(data):
        """
        Create a new student
        
        Args:
            data: Dictionary with student information
            
        Returns:
            tuple: (success, student_or_error)
        """
        # Validate data
        is_valid, error = validate_student_data(data)
        if not is_valid:
            return False, error
        
        try:
            # Check if register number already exists
            existing = Student.query.filter_by(
                register_number=data['register_number'].strip()
            ).first()
            
            if existing:
                return False, f"Student with register number {data['register_number']} already exists"
            
            # Create student
            student = Student(
                name=data['name'].strip(),
                register_number=data['register_number'].strip(),
                section=data['section'].strip(),
                department=data['department'].strip(),
                duration=data['duration'].strip()
            )
            
            db.session.add(student)
            db.session.commit()
            
            return True, student
            
        except IntegrityError as e:
            db.session.rollback()
            return False, "Database integrity error: Student may already exist"
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating student: {str(e)}"
    
    @staticmethod
    def bulk_create_students(students_data):
        """
        Create multiple students from list
        
        Args:
            students_data: List of student dictionaries
            
        Returns:
            tuple: (success_count, failed_count, errors)
        """
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
                    'row': idx + 2,  # +2 because row 1 is header, and 0-indexed
                    'register_number': data.get('register_number', 'N/A'),
                    'error': result
                })
        
        return success_count, failed_count, errors
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID"""
        return Student.query.get(student_id)
    
    @staticmethod
    def get_student_by_register_number(register_number):
        """Get student by register number"""
        return Student.query.filter_by(register_number=register_number).first()
    
    @staticmethod
    def get_all_students(filters=None):
        """
        Get all students with optional filters
        
        Args:
            filters: Dictionary with filter criteria (section, department, etc.)
            
        Returns:
            List of students
        """
        query = Student.query
        
        if filters:
            if 'section' in filters and filters['section']:
                query = query.filter_by(section=filters['section'])
            if 'department' in filters and filters['department']:
                query = query.filter_by(department=filters['department'])
            if 'duration' in filters and filters['duration']:
                query = query.filter_by(duration=filters['duration'])
            if 'has_nfc' in filters:
                if filters['has_nfc']:
                    query = query.filter(Student.nfc_tag_id.isnot(None))
                else:
                    query = query.filter(Student.nfc_tag_id.is_(None))
        
        return query.order_by(Student.register_number).all()
    
    @staticmethod
    def search_students(search_term):
        """
        Search students by name or register number
        
        Args:
            search_term: Search string
            
        Returns:
            List of matching students
        """
        search = f"%{search_term}%"
        return Student.query.filter(
            db.or_(
                Student.name.ilike(search),
                Student.register_number.ilike(search)
            )
        ).order_by(Student.register_number).all()
    
    @staticmethod
    def delete_student(student_id):
        """
        Delete a student
        
        Args:
            student_id: ID of student to delete
            
        Returns:
            tuple: (success, message)
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            db.session.delete(student)
            db.session.commit()
            return True, "Student deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting student: {str(e)}"
