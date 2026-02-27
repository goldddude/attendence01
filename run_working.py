"""
Working run script - bypasses numpy/pandas issues completely
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
from src.models import db, Student, Attendance, Faculty
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
        
        # Validate required fields
        required = ['name', 'register_number', 'section', 'department', 'duration']
        for field in required:
            if field not in data:
                return {'error': f'Missing field: {field}'}, 400
        
        # Check for duplicate register number
        existing = Student.query.filter_by(register_number=data['register_number'].strip()).first()
        if existing:
            return {'error': f"Student with register number {data['register_number']} already exists"}, 400
        
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

@app.route('/api/students/<int:student_id>', methods=['GET', 'DELETE'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {'error': 'Student not found'}, 404
    
    if request.method == 'DELETE':
        # Delete student and all their attendance records (cascade)
        db.session.delete(student)
        db.session.commit()
        return {'message': 'Student deleted successfully'}, 200
    
    return {'student': student.to_dict()}, 200

# Upload students from Excel/CSV
@app.route('/api/students/upload', methods=['POST'])
def upload_students():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        return {'error': 'Invalid file format. Only .xlsx, .xls, and .csv are supported'}, 400
    
    try:
        from io import BytesIO, StringIO
        import csv
        
        # Required columns matching student model
        required_columns = ['name', 'register_number', 'section', 'department', 'duration']
        
        rows = []
        headers = []
        
        # Read file based on extension
        if file.filename.endswith('.csv'):
            # CSV parsing
            content = file.read().decode('utf-8-sig')  # Handle BOM
            csv_reader = csv.DictReader(StringIO(content))
            headers = [h.strip().lower().replace(' ', '_') for h in csv_reader.fieldnames]
            rows = list(csv_reader)
        else:
            # Excel parsing using openpyxl
            try:
                from openpyxl import load_workbook
            except ImportError:
                return {'error': 'openpyxl not installed. Please install it: pip install openpyxl'}, 500
            
            wb = load_workbook(filename=BytesIO(file.read()), read_only=True)
            ws = wb.active
            
            # Get headers from first row
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            headers = [str(h).strip().lower().replace(' ', '_') for h in header_row if h]
            
            # Get data rows
            for row in ws.iter_rows(min_row=2, values_only=True):
                if any(cell for cell in row):  # Skip empty rows
                    row_dict = {}
                    for idx, header in enumerate(headers):
                        if idx < len(row):
                            row_dict[header] = row[idx]
                    rows.append(row_dict)
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in headers]
        if missing_columns:
            return {'error': f'Missing required columns: {", ".join(missing_columns)}'}, 400
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for index, row in enumerate(rows):
            try:
                # Get values with proper None handling
                name = row.get('name')
                register_num = row.get('register_number')
                section = row.get('section')
                department = row.get('department')
                duration = row.get('duration')
                
                # Validate required fields
                if not name or not register_num:
                    errors.append({
                        'row': index + 2,
                        'register_number': str(register_num) if register_num else 'N/A',
                        'error': 'Missing name or register number'
                    })
                    failed_count += 1
                    continue
                
                # Convert to string and strip
                register_num = str(register_num).strip()
                
                # Check if student already exists
                existing = Student.query.filter_by(register_number=register_num).first()
                if existing:
                    errors.append({
                        'row': index + 2,
                        'register_number': register_num,
                        'error': 'Student already exists'
                    })
                    failed_count += 1
                    continue
                
                # Create student with exact fields from model
                student = Student(
                    name=str(name).strip(),
                    register_number=register_num,
                    section=str(section).strip() if section else '',
                    department=str(department).strip() if department else '',
                    duration=str(duration).strip() if duration else ''
                )
                
                db.session.add(student)
                success_count += 1
                
            except Exception as e:
                errors.append({
                    'row': index + 2,
                    'register_number': str(row.get('register_number', 'N/A')),
                    'error': str(e)
                })
                failed_count += 1
        
        # Commit all successful students
        if success_count > 0:
            db.session.commit()
        
        return {
            'message': f'Upload complete: {success_count} students added, {failed_count} failed',
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }, 200
        
    except Exception as e:
        return {'error': f'Failed to process file: {str(e)}'}, 500



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
    
    # Check if tag already registered to another student
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

# ========== FACULTY API ==========

@app.route('/api/faculty/login', methods=['POST'])
def faculty_login():
    from src.models import Faculty
    import random
    from datetime import datetime
    
    data = request.get_json()
    
    if not data:
        return {'error': 'No data provided'}, 400
    
    email = data.get('email')
    name = data.get('name')
    
    if not email:
        return {'error': 'Email is required'}, 400
    
    # Generate 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Find or create faculty
    faculty = Faculty.query.filter_by(email=email).first()
    
    if not faculty:
        if not name:
            return {'error': 'Name is required for new faculty'}, 400
        
        faculty = Faculty(
            name=name,
            email=email
        )
        db.session.add(faculty)
    
    # Update OTP
    faculty.otp = otp
    faculty.otp_created_at = datetime.utcnow()
    
    db.session.commit()
    
    print(f"📧 OTP for {email}: {otp}")
    
    return {
        'message': 'OTP sent to your email',
        'email': email,
        'otp': otp
    }, 200

@app.route('/api/faculty/verify-otp', methods=['POST'])
def verify_otp():
    from src.models import Faculty
    from datetime import datetime, timedelta
    import secrets
    
    data = request.get_json()
    
    if not data:
        return {'error': 'No data provided'}, 400
    
    email = data.get('email')
    otp = data.get('otp')
    remember_me = data.get('remember_me', False)
    
    if not email or not otp:
        return {'error': 'Email and OTP are required'}, 400
    
    faculty = Faculty.query.filter_by(email=email).first()
    
    if not faculty:
        return {'error': 'Faculty not found'}, 400
    
    if not faculty.otp:
        return {'error': 'No OTP generated. Please request a new one'}, 400
    
    # Check if OTP is expired (10 minutes)
    if faculty.otp_created_at:
        otp_age = datetime.utcnow() - faculty.otp_created_at
        if otp_age > timedelta(minutes=10):
            return {'error': 'OTP expired. Please request a new one'}, 400
    
    # Verify OTP
    if faculty.otp != otp:
        return {'error': 'Invalid OTP'}, 400
    
    # Clear OTP
    faculty.otp = None
    faculty.otp_created_at = None
    
    # Generate remember token if requested
    token = None
    if remember_me:
        token = secrets.token_urlsafe(32)
        faculty.remember_token = token
        faculty.remember_expires = datetime.utcnow() + timedelta(days=30)
    
    db.session.commit()
    
    response_data = {
        'message': 'Login successful',
        'faculty': faculty.to_dict()
    }
    
    if token:
        response_data['remember_token'] = token
    
    return response_data, 200

@app.route('/api/faculty/verify-token', methods=['POST'])
def verify_token():
    from src.models import Faculty
    from datetime import datetime
    
    data = request.get_json()
    
    if not data:
        return {'error': 'No data provided'}, 400
    
    email = data.get('email')
    token = data.get('token')
    
    if not email or not token:
        return {'error': 'Email and token are required'}, 400
    
    faculty = Faculty.query.filter_by(email=email).first()
    
    if not faculty:
        return {'error': 'Faculty not found'}, 400
    
    if not faculty.remember_token or faculty.remember_token != token:
        return {'error': 'Invalid token'}, 400
    
    # Check if token is expired
    if faculty.remember_expires and faculty.remember_expires < datetime.utcnow():
        return {'error': 'Token expired. Please login again'}, 400
    
    return {
        'message': 'Token valid',
        'faculty': faculty.to_dict()
    }, 200

@app.route('/api/faculty/logout', methods=['POST'])
def faculty_logout():
    from src.models import Faculty
    
    data = request.get_json()
    
    if not data:
        return {'error': 'No data provided'}, 400
    
    email = data.get('email')
    
    if not email:
        return {'error': 'Email is required'}, 400
    
    faculty = Faculty.query.filter_by(email=email).first()
    
    if faculty:
        faculty.remember_token = None
        faculty.remember_expires = None
        db.session.commit()
    
    return {'message': 'Logged out successfully'}, 200

@app.route('/api/faculty/profile', methods=['GET'])
def get_faculty_profile():
    from src.models import Faculty
    
    email = request.args.get('email')
    
    if not email:
        return {'error': 'Email is required'}, 400
    
    faculty = Faculty.query.filter_by(email=email).first()
    
    if faculty:
        return faculty.to_dict(), 200
    else:
        return {'error': 'Faculty not found'}, 404

# ========== ATTENDANCE API ==========

@app.route('/api/attendance/record', methods=['POST'])
def record_attendance():
    from datetime import datetime, timedelta
    
    data = request.get_json()
    
    student_id = data.get('student_id')
    nfc_tag_id = data.get('nfc_tag_id')
    faculty_name = data.get('faculty_name', 'Unknown Faculty')
    section = data.get('section')
    subject = data.get('subject')
    date = data.get('date')  # Date of class
    class_time = data.get('time')  # Class time slot
    
    # Get student by NFC tag if provided
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
    
    # Check for duplicate within 1 hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.timestamp >= one_hour_ago
    ).first()
    
    if recent:
        return {'error': f"Attendance already recorded for {student.name} at {recent.timestamp.strftime('%H:%M:%S')}"}, 400
    
    # Create attendance record
    attendance = Attendance(
        student_id=student_id,
        recorded_by=faculty_name,
        section=section,
        subject=subject,
        date=date,
        class_time=class_time
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
    
    # Today's attendance
    today = datetime.utcnow().date()
    from datetime import datetime as dt
    start_of_day = dt.combine(today, dt.min.time())
    today_count = Attendance.query.filter(Attendance.timestamp >= start_of_day).count()
    
    # Unique students today
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
    
    host = '0.0.0.0'  # Listen on all interfaces
    port = 5000
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║     NFC Attendance System - Development Server        ║
    ╚═══════════════════════════════════════════════════════╝
    
    ✅ All APIs loaded successfully!
    
    🌐 Access from Computer: http://localhost:{port}
    📱 Access from Android:   http://{local_ip}:{port}
    
    🗄️  Database: SQLite (development)
    
    💡 Make sure your Android phone is on the same WiFi network!
    💡 For NFC features, use Chrome browser on Android
    
    Press CTRL+C to stop the server
    """)
    
    app.run(host=host, port=port, debug=True)
