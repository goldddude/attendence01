"""
Faculty Authentication API
REST endpoints for faculty login, OTP generation, and session management
"""
from flask import Blueprint, request, jsonify, session
from src.services.faculty_service import FacultyService
import secrets

faculty_bp = Blueprint('faculty', __name__)


@faculty_bp.route('/login', methods=['POST'])
def login():
    """Initiate login by sending OTP to email"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        name = data.get('name')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Generate and send OTP
        success, result = FacultyService.generate_otp(email, name)
        
        if success:
            return jsonify({
                'message': 'OTP sent to your email',
                'email': email,
                'otp': result  # In production, don't send OTP in response
            }), 200
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@faculty_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and create session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        otp = data.get('otp')
        remember_me = data.get('remember_me', False)
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        # Verify OTP
        success, result = FacultyService.verify_otp(email, otp, remember_me)
        
        if success:
            faculty, token = result
            response_data = {
                'message': 'Login successful',
                'faculty': faculty.to_dict()
            }
            
            if token:
                response_data['remember_token'] = token
            
            return jsonify(response_data), 200
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@faculty_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify remember me token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        token = data.get('token')
        
        if not email or not token:
            return jsonify({'error': 'Email and token are required'}), 400
        
        # Verify token
        success, result = FacultyService.verify_remember_token(email, token)
        
        if success:
            return jsonify({
                'message': 'Token valid',
                'faculty': result.to_dict()
            }), 200
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@faculty_bp.route('/logout', methods=['POST'])
def logout():
    """Logout and invalidate remember token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        FacultyService.logout(email)
        
        return jsonify({'message': 'Logged out successfully'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@faculty_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get faculty profile by email"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        faculty = FacultyService.get_faculty_by_email(email)
        
        if faculty:
            return jsonify(faculty.to_dict()), 200
        else:
            return jsonify({'error': 'Faculty not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
