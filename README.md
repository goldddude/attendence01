# TapSync Pro - NFC Attendance System

A modern, serverless NFC-based attendance management system built with Flask and deployed on Vercel.

## 🚀 Features

- **NFC-Based Attendance**: Quick and contactless attendance marking using NFC tags
- **Student Management**: Upload and manage student records via Excel
- **Faculty Dashboard**: Manage attendance sessions with subject and time tracking
- **Real-time Analytics**: View attendance reports and statistics
- **Session Management**: Create, close, and delete attendance sessions
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Vercel Serverless Functions
- **Frontend**: HTML, CSS, JavaScript
- **File Processing**: Pandas, OpenPyXL for Excel uploads

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js (for Vercel CLI)
- Git

## 🔧 Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/goldddude/Tapsyncpro.git
   cd Tapsyncpro
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the development server**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🌐 Deployment to Vercel

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository: `goldddude/Tapsyncpro`
4. Vercel will auto-detect the configuration from `vercel.json`
5. Add environment variables (if using PostgreSQL):
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure random string
6. Click "Deploy"

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

## 📊 Database Configuration

### Development (SQLite)
The app uses SQLite by default for local development. The database file is created automatically in `/tmp` for Vercel compatibility.

### Production (PostgreSQL)
For production deployment on Vercel, it's recommended to use PostgreSQL:

1. Create a PostgreSQL database (e.g., on [Supabase](https://supabase.com/), [Railway](https://railway.app/), or [Neon](https://neon.tech/))
2. Add the `DATABASE_URL` environment variable in Vercel:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

## 📁 Project Structure

```
Tapsyncpro/
├── api/
│   └── index.py              # Vercel serverless entry point
├── src/
│   ├── api/                  # API blueprints
│   │   ├── students.py       # Student management endpoints
│   │   ├── nfc.py           # NFC scanning endpoints
│   │   ├── attendance.py    # Attendance management
│   │   └── faculty.py       # Faculty authentication
│   ├── services/            # Business logic
│   ├── static/              # Frontend files
│   └── models.py            # Database models
├── tests/                   # Test files
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Production only |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `FLASK_ENV` | Environment (development/production) | No |

## 📱 Usage Guide

### For Faculty

1. **Login**: Access the faculty dashboard
2. **Create Session**: Start a new attendance session with subject details
3. **Students Scan**: Students tap their NFC tags to mark attendance
4. **View Records**: Check attendance reports and analytics
5. **Close Session**: End the session when complete

### For Students

1. **Tap NFC Tag**: Hold your NFC-enabled device near the reader
2. **Confirmation**: See instant confirmation of attendance
3. **View Status**: Check your attendance history

### For Administrators

1. **Upload Students**: Use the Excel template to bulk upload student data
2. **Manage Records**: Edit or delete student information
3. **Generate Reports**: Export attendance data for analysis

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 📝 API Endpoints

- `POST /api/students/upload` - Upload student data via Excel
- `GET /api/students` - Get all students
- `POST /api/nfc/scan` - Record NFC attendance
- `GET /api/attendance` - Get attendance records
- `POST /api/faculty/login` - Faculty authentication
- `POST /api/attendance/session` - Create attendance session
- `DELETE /api/attendance/session/:id` - Close attendance session

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions, please create an issue in the GitHub repository.

## 🔄 Version History

- **v1.0.0** - Initial release with core features
  - NFC attendance marking
  - Student management
  - Faculty dashboard
  - Excel upload functionality
  - Vercel deployment support

---

**Built with ❤️ for modern attendance management**
