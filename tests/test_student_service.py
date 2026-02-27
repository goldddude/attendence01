"""
Test Student Service
Sample test cases for student management
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import create_app
from src.models import db, Student
from src.services.student_service import StudentService


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_create_student(app):
    """Test creating a student"""
    with app.app_context():
        student_data = {
            'name': 'John Doe',
            'register_number': 'TEST001',
            'section': 'A',
            'department': 'Computer Science',
            'duration': 'Year 3'
        }
        
        success, result = StudentService.create_student(student_data)
        
        assert success is True
        assert result.name == 'John Doe'
        assert result.register_number == 'TEST001'


def test_duplicate_register_number(app):
    """Test that duplicate register numbers are rejected"""
    with app.app_context():
        student_data = {
            'name': 'John Doe',
            'register_number': 'TEST001',
            'section': 'A',
            'department': 'Computer Science',
            'duration': 'Year 3'
        }
        
        # Create first student
        success1, result1 = StudentService.create_student(student_data)
        assert success1 is True
        
        # Try to create duplicate
        success2, result2 = StudentService.create_student(student_data)
        assert success2 is False
        assert 'already exists' in result2.lower()


def test_get_all_students(app):
    """Test retrieving all students"""
    with app.app_context():
        # Create multiple students
        for i in range(3):
            student_data = {
                'name': f'Student {i}',
                'register_number': f'TEST00{i}',
                'section': 'A',
                'department': 'Computer Science',
                'duration': 'Year 3'
            }
            StudentService.create_student(student_data)
        
        students = StudentService.get_all_students()
        assert len(students) == 3


def test_search_students(app):
    """Test student search functionality"""
    with app.app_context():
        student_data = {
            'name': 'Alice Johnson',
            'register_number': 'TEST001',
            'section': 'A',
            'department': 'Computer Science',
            'duration': 'Year 3'
        }
        StudentService.create_student(student_data)
        
        # Search by name
        results = StudentService.search_students('Alice')
        assert len(results) == 1
        assert results[0].name == 'Alice Johnson'
        
        # Search by register number
        results = StudentService.search_students('TEST001')
        assert len(results) == 1


def test_filter_students_by_section(app):
    """Test filtering students by section"""
    with app.app_context():
        # Create students in different sections
        for section in ['A', 'B']:
            for i in range(2):
                student_data = {
                    'name': f'Student {section}{i}',
                    'register_number': f'TEST{section}{i}',
                    'section': section,
                    'department': 'Computer Science',
                    'duration': 'Year 3'
                }
                StudentService.create_student(student_data)
        
        # Filter by section A
        students = StudentService.get_all_students({'section': 'A'})
        assert len(students) == 2
        assert all(s.section == 'A' for s in students)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
