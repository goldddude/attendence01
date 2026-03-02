"""
NFC Attendance System - Entry Point
Run this file to start the Flask development server
"""
import os
from dotenv import load_dotenv
from src.app import create_app

# Load environment variables from .env file (if present)
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))

    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║     NFC Attendance System - Development Server        ║
    ╚═══════════════════════════════════════════════════════╝

    🌐 Server running at: http://localhost:{port}
    📱 For NFC features, access from Android Chrome via HTTPS
    🗄️  Database: MongoDB Atlas

    Press CTRL+C to stop the server
    """)

    # use_reloader=False prevents double-init of MongoDB singleton
    app.run(host=host, port=port, debug=True, use_reloader=False)
