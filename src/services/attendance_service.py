"""
Attendance Management Service
Business logic for attendance operations
"""
from datetime import datetime, timedelta
from src.models import db, Attendance, Student
from sqlalchemy import func


class AttendanceService:
    """Service class for attendance management"""
    
    @staticmethod
    def record_attendance(student_id, faculty_name, section=None, subject=None):
        """
        Record attendance for a student
        
        Args:
            student_id: ID of the student
            faculty_name: Name of the faculty recording attendance
            section: Section (e.g., S-01, S-02)
            subject: Subject name
            
        Returns:
            tuple: (success, message_or_attendance)
        """
        try:
            # Verify student exists
            student = Student.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            # Check if already marked today (prevent duplicates within 1 hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_attendance = Attendance.query.filter(
                Attendance.student_id == student_id,
                Attendance.timestamp >= one_hour_ago
            ).first()
            
            if recent_attendance:
                return False, f"Attendance already recorded for {student.name} at {recent_attendance.timestamp.strftime('%H:%M:%S')}"
            
            # Create attendance record
            attendance = Attendance(
                student_id=student_id,
                recorded_by=faculty_name,
                section=section,
                subject=subject
            )
            
            db.session.add(attendance)
            db.session.commit()
            
            return True, attendance
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error recording attendance: {str(e)}"
    
    @staticmethod
    def get_attendance_by_student(student_id, limit=None):
        """
        Get attendance records for a student
        
        Args:
            student_id: ID of the student
            limit: Maximum number of records to return (optional)
            
        Returns:
            List of attendance records
        """
        query = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_recent_attendance(limit=50):
        """
        Get recent attendance records across all students
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of attendance records
        """
        return Attendance.query.order_by(Attendance.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_attendance_by_date(date=None):
        """
        Get attendance records for a specific date
        
        Args:
            date: Date object (defaults to today)
            
        Returns:
            List of attendance records
        """
        if date is None:
            date = datetime.utcnow().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        return Attendance.query.filter(
            Attendance.timestamp >= start_of_day,
            Attendance.timestamp <= end_of_day
        ).order_by(Attendance.timestamp.desc()).all()
    
    @staticmethod
    def get_attendance_stats():
        """
        Get attendance statistics
        
        Returns:
            Dictionary with statistics
        """
        total_students = Student.query.count()
        total_records = Attendance.query.count()
        
        # Today's attendance
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        today_count = Attendance.query.filter(Attendance.timestamp >= start_of_day).count()
        
        # Unique students who attended today
        today_students = db.session.query(Attendance.student_id).filter(
            Attendance.timestamp >= start_of_day
        ).distinct().count()
        
        return {
            'total_students': total_students,
            'total_attendance_records': total_records,
            'today_attendance_count': today_count,
            'today_unique_students': today_students,
            'today_percentage': round((today_students / total_students * 100) if total_students > 0 else 0, 2)
        }
