"""
Vercel serverless function entry point
This file makes your Flask app compatible with Vercel's serverless architecture
"""
import os
import sys

# Move to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

# Create Flask app
static_folder = os.path.join(BASE_DIR, 'src', 'static')
app = Flask(__name__, static_folder=static_folder, static_url_path='')

# Configuration
# Vercel's filesystem is READ-ONLY. If using SQLite, we MUST use /tmp
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Use /tmp for SQLite to prevent "ReadOnly" crash, but data won't persist between requests
    database_url = 'sqlite:///' + os.path.join('/tmp', 'nfc_attendance.db')
elif database_url.startswith('postgres://'):
    # Fix for newer SQLAlchemy versions which require 'postgresql://' instead of 'postgres://'
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CORS
CORS(app)

# Import and initialize database
from src.models import db
db.init_app(app)

# Create database tables (Safe for serverless)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database creation warning: {e}")

# Register blueprints
from src.api.students import students_bp
from src.api.nfc import nfc_bp
from src.api.attendance import attendance_bp
from src.api.faculty import faculty_bp

app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(nfc_bp, url_prefix='/api/nfc')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(faculty_bp, url_prefix='/api/faculty')

# Frontend routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Try to serve the static file, but fallback to index.html for SPA-style routing
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Vercel requires the WSGI app to be named 'handler'
handler = app
