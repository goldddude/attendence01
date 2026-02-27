"""
NFC Attendance System - Entry Point
Run this file to start the Flask development server
"""
import os
from dotenv import load_dotenv
from src.app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment variables
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
