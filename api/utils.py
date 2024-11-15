import re
import uuid
import jwt
from flask import request
import secrets
import auth

def validate_organization_name(name):
    """Validate organization name format and length"""
    if not name or not isinstance(name, str):
        return False, "Organization name is required and must be a string"
    
    if len(name.strip()) < 3 or len(name.strip()) > 100:
        return False, "Organization name must be between 3 and 100 characters"
    
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return False, "Organization name can only contain letters, numbers, spaces, hyphens, and underscores"
    
    return True, None

def validate_uuid(uuid_string):
    """Validate UUID format"""
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return True, None
    except ValueError:
        return False, "Invalid UUID format"

def validate_username(username):
    """Validate username format and length"""
    if not username or not isinstance(username, str):
        return False, "Username is required and must be a string"
    
    if len(username.strip()) < 3 or len(username.strip()) > 50:
        return False, "Username must be between 3 and 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_\-\.@]+$', username):
        return False, "Username can only contain letters, numbers, dots, @, hyphens, and underscores"
    
    return True, None

def validate_password(password):
    """Validate password strength and format"""
    if not password or not isinstance(password, str):
        return False, "Password is required and must be a string"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_token(token, secret_key):
    """Validate JWT token format"""
    if not token or not isinstance(token, str):
        return False, "Token is required and must be a string"
    
    try:
        jwt.decode(token, secret_key, algorithms=["HS256"])
        return True, None
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token format"

def validate_request_data(request):
    """Validate request data format"""
    if not hasattr(request, 'get_json'):
        return None, "Invalid request format"
    
    try:
        data = request.get_json()
    except Exception as e:
        return None, f"Invalid JSON format: {str(e)}"
    
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"
    
    return data, None

def get_user_from_token(request, secret_key):
    """Extract username from authorized token"""
    if not hasattr(request, 'headers'):
        return None
    
    token = request.headers.get('x-access-token')
    if not token or not isinstance(token, str):
        return None
    
    try:
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = data.get('username')
        if not username or not isinstance(username, str):
            return None
        return username
    except:
        return None