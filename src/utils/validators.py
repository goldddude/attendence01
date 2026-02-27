"""
Input validation utilities
"""
import re


def validate_student_data(data):
    """
    Validate student data
    
    Args:
        data: Dictionary with student information
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['name', 'register_number', 'section', 'department', 'duration']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate name (letters, spaces, dots only)
    if not re.match(r'^[A-Za-z\s.]+$', data['name'].strip()):
        return False, "Name should contain only letters, spaces, and dots"
    
    # Validate register number (alphanumeric)
    if not re.match(r'^[A-Za-z0-9]+$', data['register_number'].strip()):
        return False, "Register number should be alphanumeric"
    
    # Validate section (alphanumeric)
    if not re.match(r'^[A-Za-z0-9]+$', data['section'].strip()):
        return False, "Section should be alphanumeric"
    
    return True, None


def validate_nfc_tag(tag_id):
    """
    Validate NFC tag ID
    
    Args:
        tag_id: NFC tag identifier
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not tag_id or not tag_id.strip():
        return False, "NFC tag ID cannot be empty"
    
    # NFC tag IDs are typically hex strings
    if not re.match(r'^[A-Fa-f0-9:]+$', tag_id.strip()):
        return False, "Invalid NFC tag ID format"
    
    return True, None
