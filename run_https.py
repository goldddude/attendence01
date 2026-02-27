"""
Run TapSyncPro with HTTPS using adhoc SSL (simple, no dependencies)
"""
import os
import sys

# Set environment
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, static_folder='src/static', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfc_attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CORS
CORS(app)

# Import and initialize database
from src.models import db, Student, Attendance
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully")

# ========== FRONTEND ROUTES ==========

@app.route('/')
def index():
    return send_from_directory('src/static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('src/static', path)
    except:
        return send_from_directory('src/static', 'index.html')

# Serve Excel template
@app.route('/sample_students_template.xlsx')
def download_template():
    from flask import send_file
    template_path = os.path.join(os.path.dirname(__file__), 'sample_students_template.xlsx')
    if os.path.exists(template_path):
        return send_file(template_path, as_attachment=True, download_name='sample_students_template.xlsx')
    return {'error': 'Template not found'}, 404

# ========== STUDENT API ==========

@app.route('/api/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        data = request.get_json()
        
        required = ['name', 'register_number', 'section', 'department', 'duration']
        for field in required:
            if field not in data:
                return {'error': f'Missing field: {field}'}, 400
        
        existing = Student.query.filter_by(register_number=data['register_number'].strip()).first()
        if existing:
            return {'error': f"Student with register number {data['register_number']} already exists"}, 400
        
        student = Student(
            name=data['name'].strip(),
            register_number=data['register_number'].strip(),
            section=data['section'].strip(),
            department=data['department'].strip(),
            duration=data['duration'].strip()
        )
        
        db.session.add(student)
        db.session.commit()
        
        return {'message': 'Student created successfully', 'student': student.to_dict()}, 201
    
    else:  # GET
        search = request.args.get('search')
        section = request.args.get('section')
        has_nfc = request.args.get('has_nfc')
        
        query = Student.query
        
        if search:
            query = query.filter(db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.register_number.ilike(f'%{search}%')
            ))
        
        if section:
            query = query.filter_by(section=section)
        
        if has_nfc:
            if has_nfc.lower() == 'true':
                query = query.filter(Student.nfc_tag_id.isnot(None))
            else:
                query = query.filter(Student.nfc_tag_id.is_(None))
        
        students = query.order_by(Student.register_number).all()
        
        return {
            'count': len(students),
            'students': [s.to_dict() for s in students]
        }, 200

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {'error': 'Student not found'}, 404
    return {'student': student.to_dict()}, 200

# ========== NFC API ==========

@app.route('/api/nfc/register', methods=['POST'])
def register_nfc():
    data = request.get_json()
    
    student_id = data.get('student_id')
    nfc_tag_id = data.get('nfc_tag_id')
    
    if not student_id or not nfc_tag_id:
        return {'error': 'student_id and nfc_tag_id are required'}, 400
    
    student = Student.query.get(student_id)
    if not student:
        return {'error': 'Student not found'}, 404
    
    existing = Student.query.filter_by(nfc_tag_id=nfc_tag_id.strip()).first()
    if existing and existing.id != student_id:
        return {'error': f'NFC tag already registered to {existing.name}'}, 400
    
    student.nfc_tag_id = nfc_tag_id.strip()
    db.session.commit()
    
    return {'message': 'NFC tag registered successfully', 'student': student.to_dict()}, 200

@app.route('/api/nfc/student/<nfc_tag_id>', methods=['GET'])
def get_student_by_tag(nfc_tag_id):
    student = Student.query.filter_by(nfc_tag_id=nfc_tag_id).first()
    if not student:
        return {'error': 'No student found with this NFC tag'}, 404
    return {'student': student.to_dict()}, 200

# ========== ATTENDANCE API ==========

@app.route('/api/attendance/record', methods=['POST'])
def record_attendance():
    from datetime import datetime, timedelta
    
    data = request.get_json()
    
    student_id = data.get('student_id')
    nfc_tag_id = data.get('nfc_tag_id')
    faculty_name = data.get('faculty_name', 'Unknown Faculty')
    
    if nfc_tag_id and not student_id:
        student = Student.query.filter_by(nfc_tag_id=nfc_tag_id).first()
        if not student:
            return {'error': 'No student found with this NFC tag'}, 404
        student_id = student.id
    
    if not student_id:
        return {'error': 'student_id or nfc_tag_id is required'}, 400
    
    student = Student.query.get(student_id)
    if not student:
        return {'error': 'Student not found'}, 404
    
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.timestamp >= one_hour_ago
    ).first()
    
    if recent:
        return {'error': f"Attendance already recorded for {student.name} at {recent.timestamp.strftime('%H:%M:%S')}"}, 400
    
    attendance = Attendance(
        student_id=student_id,
        recorded_by=faculty_name
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return {'message': 'Attendance recorded successfully', 'attendance': attendance.to_dict()}, 201

@app.route('/api/attendance/student/<int:student_id>', methods=['GET'])
def get_student_attendance(student_id):
    limit = request.args.get('limit', type=int)
    query = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.timestamp.desc())
    
    if limit:
        query = query.limit(limit)
    
    records = query.all()
    
    return {
        'count': len(records),
        'attendance': [r.to_dict() for r in records]
    }, 200

@app.route('/api/attendance/recent', methods=['GET'])
def get_recent_attendance():
    limit = request.args.get('limit', 50, type=int)
    records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(limit).all()
    
    return {
        'count': len(records),
        'attendance': [r.to_dict() for r in records]
    }, 200

@app.route('/api/attendance/stats', methods=['GET'])
def get_stats():
    from datetime import datetime
    
    total_students = Student.query.count()
    total_records = Attendance.query.count()
    
    today = datetime.utcnow().date()
    from datetime import datetime as dt
    start_of_day = dt.combine(today, dt.min.time())
    today_count = Attendance.query.filter(Attendance.timestamp >= start_of_day).count()
    
    today_students = db.session.query(Attendance.student_id).filter(
        Attendance.timestamp >= start_of_day
    ).distinct().count()
    
    return {
        'total_students': total_students,
        'total_attendance_records': total_records,
        'today_attendance_count': today_count,
        'today_unique_students': today_students,
        'today_percentage': round((today_students / total_students * 100) if total_students > 0 else 0, 2)
    }, 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def server_error(e):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    import socket
    
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "Unable to detect"
    
    host = '0.0.0.0'
    port = 5000
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║     TapSyncPro - HTTPS Development Server            ║
    ╚═══════════════════════════════════════════════════════╝
    
    ✅ All APIs loaded successfully!
    🔒 HTTPS enabled (ad-hoc SSL certificate)
    
    🌐 Access from Computer: https://localhost:{port}
    📱 Access from Android:   https://{local_ip}:{port}
    
    🗄️  Database: SQLite (development)
    
    ⚠️  IMPORTANT FOR ANDROID NFC:
    
    1. On Samsung A55, open Chrome
    2. Go to: https://{local_ip}:{port}
    3. You'll see: "Your connection is not private"
    4. Click "Advanced"
    5. Click "Proceed to {local_ip} (unsafe)"
    6. NFC will now work! ✅
    
    💡 The security warning is normal for development
    💡 This uses a temporary self-signed certificate
    
    Press CTRL+C to stop the server
    """)
    
    # Run with ad-hoc SSL (Flask's built-in)
    app.run(host=host, port=port, debug=True, ssl_context='adhoc')
