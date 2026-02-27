"""
Alternative run script that works around numpy import issues
"""
import os
import sys

# Set environment before any other imports
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using defaults")

from flask import Flask, send_from_directory
from flask_cors import CORS

# Create minimal app without pandas dependency for now
app = Flask(__name__, static_folder='src/static', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
database_url = os.getenv('DATABASE_URL')
if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfc_attendance.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)

# Import and initialize database
from src.models import db
db.init_app(app)

# Import blueprints (this is where pandas import happens)
try:
    from src.api.students import students_bp
    from src.api.nfc import nfc_bp
    from src.api.attendance import attendance_bp
    from src.api.faculty import faculty_bp
    
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(nfc_bp, url_prefix='/api/nfc')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(faculty_bp, url_prefix='/api/faculty')
    print("✅ All API blueprints registered successfully (including faculty)")
except ImportError as e:
    print(f"⚠️  Warning: Could not import all blueprints: {e}")
    print("⚠️  Excel upload feature may not work, but other features will function")

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('src/static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('src/static', path)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def server_error(e):
    return {'error': 'Internal server error'}, 500

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully")

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║     NFC Attendance System - Development Server        ║
    ╚═══════════════════════════════════════════════════════╝
    
    🌐 Server running at: http://localhost:{port}
    📱 For NFC features, access from Android Chrome via HTTPS
    🗄️  Database: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite (development)'}
    
    Press CTRL+C to stop the server
    """)
    
    app.run(host=host, port=port, debug=debug)
