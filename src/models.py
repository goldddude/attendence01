"""
MongoDB Database for NFC Attendance System
Uses PyMongo for database operations
"""
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
import os


_client = None
_db = None


def get_db():
    """Get MongoDB database instance (singleton)"""
    global _client, _db
    if _db is None:
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://sudhamadb:8qZcUxPko58vDYvo@cluster0.gsoxjjt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db_name = os.getenv('MONGODB_DB', 'nfc_attendance')
        _db = _client[db_name]
        # Create indexes in background so startup is not blocked
        import threading
        threading.Thread(target=_ensure_indexes, args=(_db,), daemon=True).start()
    return _db


def _ensure_indexes(db):
    """Create indexes for performance"""
    try:
        db.students.create_index([('register_number', ASCENDING)], unique=True)
        db.students.create_index([('nfc_tag_id', ASCENDING)], sparse=True)
        db.faculty.create_index([('email', ASCENDING)], unique=True)
        db.attendance.create_index([('student_id', ASCENDING)])
        db.attendance.create_index([('timestamp', DESCENDING)])
        db.attendance.create_index([('date', ASCENDING)])
        db.attendance.create_index([('section', ASCENDING)])
        db.attendance.create_index([('subject', ASCENDING)])
    except Exception as e:
        print(f"⚠️  Index creation warning: {e}")


def obj_id(id_str):
    """Convert string to ObjectId safely"""
    try:
        return ObjectId(str(id_str))
    except Exception:
        return None


# ─────────────────────────────────────────────
# Helper: Student document → dict
# ─────────────────────────────────────────────
def student_to_dict(doc):
    if not doc:
        return None
    return {
        'id': str(doc['_id']),
        'name': doc.get('name', ''),
        'register_number': doc.get('register_number', ''),
        'section': doc.get('section', ''),
        'department': doc.get('department', ''),
        'duration': doc.get('duration', ''),
        'nfc_tag_id': doc.get('nfc_tag_id'),
        'has_nfc': bool(doc.get('nfc_tag_id')),
        'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
        'updated_at': doc['updated_at'].isoformat() if doc.get('updated_at') else None,
    }


# ─────────────────────────────────────────────
# Helper: Faculty document → dict
# ─────────────────────────────────────────────
def faculty_to_dict(doc):
    if not doc:
        return None
    sections = doc.get('sections', '')
    return {
        'id': str(doc['_id']),
        'name': doc.get('name', ''),
        'email': doc.get('email', ''),
        'sections': sections.split(',') if sections else [],
        'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
    }


# ─────────────────────────────────────────────
# Helper: Attendance document → dict
# ─────────────────────────────────────────────
def attendance_to_dict(doc, student_doc=None):
    if not doc:
        return None
    # If student_doc not passed, fetch it
    if student_doc is None:
        db = get_db()
        student_doc = db.students.find_one({'_id': doc.get('student_id')})

    return {
        'id': str(doc['_id']),
        'student_id': str(doc.get('student_id', '')),
        'student_name': student_doc.get('name') if student_doc else None,
        'register_number': student_doc.get('register_number') if student_doc else None,
        'timestamp': doc['timestamp'].isoformat() if doc.get('timestamp') else None,
        'recorded_by': doc.get('recorded_by', ''),
        'section': doc.get('section'),
        'subject': doc.get('subject'),
        'date': doc.get('date'),
        'class_time': doc.get('class_time'),
    }
