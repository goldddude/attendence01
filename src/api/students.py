"""
Student Management API
REST endpoints for student operations
"""
from flask import Blueprint, request, jsonify
from src.services.student_service import StudentService
from src.utils.excel_parser import parse_student_file
import os
from werkzeug.utils import secure_filename

students_bp = Blueprint('students', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@students_bp.route('', methods=['POST'])
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success, result = StudentService.create_student(data)
        
        if success:
            return jsonify({
                'message': 'Student created successfully',
                'student': result.to_dict()
            }), 201
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@students_bp.route('/upload', methods=['POST'])
def upload_students():
    """Upload students from Excel/CSV file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload .xlsx, .xls, or .csv'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Determine file type
        file_type = 'excel' if filename.endswith(('.xlsx', '.xls')) else 'csv'
        
        # Parse file
        success, result = parse_student_file(filepath, file_type)
        
        # Clean up
        os.remove(filepath)
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Bulk create students
        success_count, failed_count, errors = StudentService.bulk_create_students(result)
        
        return jsonify({
            'message': f'Upload completed: {success_count} students added, {failed_count} failed',
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }), 201 if success_count > 0 else 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@students_bp.route('', methods=['GET'])
def get_students():
    """Get all students with optional filters"""
    try:
        # Get query parameters
        filters = {}
        if request.args.get('section'):
            filters['section'] = request.args.get('section')
        if request.args.get('department'):
            filters['department'] = request.args.get('department')
        if request.args.get('duration'):
            filters['duration'] = request.args.get('duration')
        if request.args.get('has_nfc'):
            filters['has_nfc'] = request.args.get('has_nfc').lower() == 'true'
        
        # Search functionality
        search = request.args.get('search')
        if search:
            students = StudentService.search_students(search)
        else:
            students = StudentService.get_all_students(filters)
        
        return jsonify({
            'count': len(students),
            'students': [s.to_dict() for s in students]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@students_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student by ID"""
    try:
        student = StudentService.get_student_by_id(student_id)
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify({'student': student.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    try:
        success, message = StudentService.delete_student(student_id)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
