"""
Vercel serverless function entry point.
This file makes your Flask app compatible with Vercel's serverless architecture.
"""
import os
import sys

# Add the project root to the path so all src.* imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_vercel_app():
    static_folder = os.path.join(BASE_DIR, 'src', 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='')

    # -- Database URL -------------------------------------------------------
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Vercel filesystem is read-only except /tmp — use /tmp for SQLite
        database_url = 'sqlite:///' + os.path.join('/tmp', 'nfc_attendance.db')
    elif database_url.startswith('postgres://'):
        # SQLAlchemy 1.4+ requires 'postgresql://' not 'postgres://'
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Disable connection pooling (important for serverless — each request is independent)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

    # -- Extensions ---------------------------------------------------------
    CORS(app)

    from src.models import db
    db.init_app(app)

    # -- Blueprints ---------------------------------------------------------
    from src.api.students import students_bp
    from src.api.nfc import nfc_bp
    from src.api.attendance import attendance_bp
    from src.api.faculty import faculty_bp

    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(nfc_bp, url_prefix='/api/nfc')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(faculty_bp, url_prefix='/api/faculty')

    # -- Create tables (safe for serverless, errors are non-fatal) ----------
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[WARN] db.create_all() failed: {e}")

    # -- Frontend routes ----------------------------------------------------
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        full = os.path.join(app.static_folder, path)
        if os.path.exists(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # -- Global error handler so crashes return JSON, not HTML --------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

    return app


# Build the app at module level (Vercel imports this module once per cold start)
app = create_vercel_app()

# Vercel requires the WSGI handler to be named 'handler'
handler = app
