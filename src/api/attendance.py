"""
Attendance Management API
REST endpoints for attendance operations (MongoDB)
"""
from flask import Blueprint, request, jsonify
from src.services.attendance_service import AttendanceService
from src.services.nfc_service import NFCService
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/record', methods=['POST'])
def record_attendance():
    """Record attendance for a student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        student_id = data.get('student_id')
        nfc_tag_id = data.get('nfc_tag_id')
        faculty_name = data.get('faculty_name', 'Unknown Faculty')
        section = data.get('section')
        subject = data.get('subject')
        date = data.get('date')
        class_time = data.get('time') or data.get('class_time')

        # If NFC tag provided, resolve to student
        if nfc_tag_id and not student_id:
            student_doc = NFCService.get_student_by_tag(nfc_tag_id)
            if not student_doc:
                return jsonify({'error': 'No student found with this NFC tag'}), 404
            student_id = str(student_doc['_id'])

        if not student_id:
            return jsonify({'error': 'student_id or nfc_tag_id is required'}), 400

        success, result = AttendanceService.record_attendance(
            student_id, faculty_name,
            section=section, subject=subject,
            date=date, class_time=class_time
        )

        if success:
            return jsonify({'message': 'Attendance recorded successfully', 'attendance': result}), 201
        else:
            return jsonify({'error': result}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/student/<string:student_id>', methods=['GET'])
def get_student_attendance(student_id):
    """Get attendance history for a student"""
    try:
        limit = request.args.get('limit', type=int)
        records = AttendanceService.get_attendance_by_student(student_id, limit)
        return jsonify({'count': len(records), 'attendance': records}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/recent', methods=['GET'])
def get_recent_attendance():
    """Get recent attendance records"""
    try:
        limit = request.args.get('limit', 50, type=int)
        records = AttendanceService.get_recent_attendance(limit)
        return jsonify({'count': len(records), 'attendance': records}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/date', methods=['GET'])
def get_attendance_by_date():
    """Get attendance for a specific date"""
    try:
        date_str = request.args.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = None

        records = AttendanceService.get_attendance_by_date(date)
        return jsonify({
            'date': date.isoformat() if date else datetime.utcnow().date().isoformat(),
            'count': len(records),
            'attendance': records
        }), 200

    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get attendance statistics"""
    try:
        stats = AttendanceService.get_attendance_stats()
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/all', methods=['GET'])
def get_all_attendance():
    """Get all attendance records with optional filters"""
    try:
        filters = {}
        if request.args.get('section'):
            filters['section'] = request.args.get('section')
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        if request.args.get('date'):
            filters['date'] = request.args.get('date')

        limit = request.args.get('limit', 500, type=int)
        records = AttendanceService.get_all_attendance(filters, limit)
        return jsonify({'count': len(records), 'attendance': records}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get attendance records grouped by class session"""
    try:
        sessions = AttendanceService.get_sessions()
        return jsonify({'count': len(sessions), 'sessions': sessions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/session-detail', methods=['GET'])
def get_session_detail():
    """Get all attendance records for a specific class session"""
    try:
        date = request.args.get('date')
        section = request.args.get('section')
        subject = request.args.get('subject')
        class_time = request.args.get('class_time')

        records = AttendanceService.get_session_detail(date, section, subject, class_time)
        return jsonify({'count': len(records), 'attendance': records}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
