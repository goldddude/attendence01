"""
Flask Application Factory
Configures database, CORS, and registers API blueprints
"""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models import db


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - auto-detect SQLite vs PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Production: Use PostgreSQL
        # Handle both postgres:// and postgresql:// schemes
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development: Use SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfc_attendance.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
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
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)
    
    # Serve sample Excel template from root directory
    @app.route('/sample_students_template.xlsx')
    def download_template():
        import os
        from flask import send_file
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_students_template.xlsx')
        return send_file(template_path, as_attachment=True, download_name='sample_students_template.xlsx')
    
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
    
    return app
