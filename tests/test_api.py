"""
Test API Endpoints
Sample test cases for REST API
"""
import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import create_app
from src.models import db


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


def test_create_student_api(client):
    """Test POST /api/students"""
    student_data = {
        'name': 'John Doe',
        'register_number': 'API001',
        'section': 'A',
        'department': 'Computer Science',
        'duration': 'Year 3'
    }
    
    response = client.post(
        '/api/students',
        data=json.dumps(student_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['student']['name'] == 'John Doe'


def test_get_students_api(client):
    """Test GET /api/students"""
    # Create a student first
    student_data = {
        'name': 'Jane Doe',
        'register_number': 'API002',
        'section': 'B',
        'department': 'Electronics',
        'duration': 'Year 2'
    }
    
    client.post(
        '/api/students',
        data=json.dumps(student_data),
        content_type='application/json'
    )
    
    # Get all students
    response = client.get('/api/students')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['count'] >= 1


def test_get_student_by_id_api(client):
    """Test GET /api/students/<id>"""
    # Create a student
    student_data = {
        'name': 'Test Student',
        'register_number': 'API003',
        'section': 'A',
        'department': 'Computer Science',
        'duration': 'Year 1'
    }
    
    create_response = client.post(
        '/api/students',
        data=json.dumps(student_data),
        content_type='application/json'
    )
    
    student_id = json.loads(create_response.data)['student']['id']
    
    # Get student by ID
    response = client.get(f'/api/students/{student_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['student']['register_number'] == 'API003'


def test_attendance_stats_api(client):
    """Test GET /api/attendance/stats"""
    response = client.get('/api/attendance/stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total_students' in data
    assert 'today_attendance_count' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
