"""
Vercel serverless function entry point.
Uses MongoDB (PyMongo) — no SQLAlchemy/SQLite.
"""
import os
import sys

# Add the project root to path so src.* imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

def create_vercel_app():
    static_folder = os.path.join(BASE_DIR, 'src', 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    CORS(app)

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
        full = os.path.join(app.static_folder, path)
        if os.path.exists(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # Global error handler — returns JSON so crashes don't show HTML
    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

    return app


# Vercel detects Flask WSGI apps via the `app` variable name
app = create_vercel_app()
