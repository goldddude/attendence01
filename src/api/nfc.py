"""
NFC Tag Management API
REST endpoints for NFC operations
"""
from flask import Blueprint, request, jsonify
from src.services.nfc_service import NFCService

nfc_bp = Blueprint('nfc', __name__)


@nfc_bp.route('/register', methods=['POST'])
def register_tag():
    """Register an NFC tag to a student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        student_id = data.get('student_id')
        nfc_tag_id = data.get('nfc_tag_id')
        
        if not student_id or not nfc_tag_id:
            return jsonify({'error': 'student_id and nfc_tag_id are required'}), 400
        
        success, result = NFCService.register_tag(student_id, nfc_tag_id)
        
        if success:
            return jsonify({
                'message': 'NFC tag registered successfully',
                'student': result.to_dict()
            }), 200
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfc_bp.route('/unregister/<int:student_id>', methods=['POST'])
def unregister_tag(student_id):
    """Remove NFC tag from a student"""
    try:
        success, message = NFCService.unregister_tag(student_id)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfc_bp.route('/student/<nfc_tag_id>', methods=['GET'])
def get_student_by_tag(nfc_tag_id):
    """Get student information by NFC tag ID"""
    try:
        student = NFCService.get_student_by_tag(nfc_tag_id)
        
        if not student:
            return jsonify({'error': 'No student found with this NFC tag'}), 404
        
        return jsonify({'student': student.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@nfc_bp.route('/check/<nfc_tag_id>', methods=['GET'])
def check_tag(nfc_tag_id):
    """Check if an NFC tag is registered"""
    try:
        is_registered = NFCService.is_tag_registered(nfc_tag_id)
        
        return jsonify({
            'nfc_tag_id': nfc_tag_id,
            'is_registered': is_registered
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
