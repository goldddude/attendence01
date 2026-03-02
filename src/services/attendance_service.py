"""
Attendance Management Service
Business logic for attendance operations (MongoDB)
"""
from datetime import datetime, timedelta
from bson import ObjectId
from src.models import get_db, attendance_to_dict, obj_id


class AttendanceService:
    """Service class for attendance management using MongoDB"""

    @staticmethod
    def record_attendance(student_id, faculty_name, section=None, subject=None, date=None, class_time=None):
        """Record attendance for a student"""
        try:
            db = get_db()
            oid = obj_id(student_id)
            if not oid:
                return False, "Invalid student ID"

            student = db.students.find_one({'_id': oid})
            if not student:
                return False, "Student not found"

            # Prevent duplicates within 1 hour for same session
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            dup_query = {
                'student_id': oid,
                'timestamp': {'$gte': one_hour_ago}
            }
            if section:
                dup_query['section'] = section
            if subject:
                dup_query['subject'] = subject

            recent = db.attendance.find_one(dup_query)
            if recent:
                ts = recent['timestamp'].strftime('%H:%M:%S')
                return False, f"Attendance already recorded for {student['name']} at {ts}"

            now = datetime.utcnow()
            doc = {
                'student_id': oid,
                'timestamp': now,
                'recorded_by': faculty_name,
                'section': section,
                'subject': subject,
                'date': date or now.strftime('%Y-%m-%d'),
                'class_time': class_time,
            }

            result = db.attendance.insert_one(doc)
            doc['_id'] = result.inserted_id

            return True, attendance_to_dict(doc, student)

        except Exception as e:
            return False, f"Error recording attendance: {str(e)}"

    @staticmethod
    def get_attendance_by_student(student_id, limit=None):
        """Get attendance records for a student"""
        db = get_db()
        oid = obj_id(student_id)
        if not oid:
            return []

        student = db.students.find_one({'_id': oid})
        cursor = db.attendance.find({'student_id': oid}).sort('timestamp', -1)
        if limit:
            cursor = cursor.limit(limit)

        return [attendance_to_dict(d, student) for d in cursor]

    @staticmethod
    def get_recent_attendance(limit=50):
        """Get recent attendance records across all students"""
        db = get_db()
        docs = db.attendance.find().sort('timestamp', -1).limit(limit)
        result = []
        for doc in docs:
            student = db.students.find_one({'_id': doc.get('student_id')})
            result.append(attendance_to_dict(doc, student))
        return result

    @staticmethod
    def get_attendance_by_date(date=None):
        """Get attendance records for a specific date"""
        db = get_db()
        if date is None:
            date = datetime.utcnow().date()

        date_str = date.strftime('%Y-%m-%d')
        docs = db.attendance.find({'date': date_str}).sort('timestamp', -1)

        result = []
        for doc in docs:
            student = db.students.find_one({'_id': doc.get('student_id')})
            result.append(attendance_to_dict(doc, student))
        return result

    @staticmethod
    def get_attendance_stats():
        """Get attendance statistics"""
        db = get_db()
        total_students = db.students.count_documents({})
        total_records = db.attendance.count_documents({})

        today = datetime.utcnow().strftime('%Y-%m-%d')
        today_count = db.attendance.count_documents({'date': today})

        # Unique students today
        pipeline = [
            {'$match': {'date': today}},
            {'$group': {'_id': '$student_id'}},
            {'$count': 'total'}
        ]
        agg = list(db.attendance.aggregate(pipeline))
        today_students = agg[0]['total'] if agg else 0

        return {
            'total_students': total_students,
            'total_attendance_records': total_records,
            'today_attendance_count': today_count,
            'today_unique_students': today_students,
            'today_percentage': round((today_students / total_students * 100) if total_students > 0 else 0, 2)
        }

    @staticmethod
    def get_all_attendance(filters=None, limit=500):
        """Get all attendance with optional filters"""
        db = get_db()
        query = {}
        if filters:
            if filters.get('section'):
                query['section'] = filters['section']
            if filters.get('subject'):
                query['subject'] = filters['subject']
            if filters.get('date'):
                query['date'] = filters['date']

        docs = db.attendance.find(query).sort('timestamp', -1).limit(limit)
        result = []
        for doc in docs:
            student = db.students.find_one({'_id': doc.get('student_id')})
            result.append(attendance_to_dict(doc, student))
        return result

    @staticmethod
    def get_sessions():
        """Get attendance grouped by class session"""
        db = get_db()
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'date': '$date',
                        'section': '$section',
                        'subject': '$subject',
                        'class_time': '$class_time',
                        'recorded_by': '$recorded_by',
                    },
                    'count': {'$sum': 1},
                    'first_recorded': {'$min': '$timestamp'}
                }
            },
            {'$sort': {'first_recorded': -1}}
        ]

        sessions = []
        for doc in db.attendance.aggregate(pipeline):
            g = doc['_id']
            sessions.append({
                'date': g.get('date'),
                'section': g.get('section'),
                'subject': g.get('subject'),
                'class_time': g.get('class_time'),
                'recorded_by': g.get('recorded_by'),
                'student_count': doc['count'],
                'first_recorded': doc['first_recorded'].isoformat() if doc.get('first_recorded') else None
            })

        return sessions

    @staticmethod
    def get_session_detail(date=None, section=None, subject=None, class_time=None):
        """Get attendance records for a specific session"""
        db = get_db()
        query = {}
        if date:
            query['date'] = date
        if section:
            query['section'] = section
        if subject:
            query['subject'] = subject
        if class_time:
            query['class_time'] = class_time

        docs = db.attendance.find(query).sort('timestamp', 1)
        result = []
        for doc in docs:
            student = db.students.find_one({'_id': doc.get('student_id')})
            result.append(attendance_to_dict(doc, student))
        return result
