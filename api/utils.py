import re
import uuid
import jwt
from flask import request
import auth
from google.cloud import secretmanager
import os
from database import get_user_credentials as db_get_user_credentials

project_id = os.environ.get('GCP_PROJECT')

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

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
    if len(uuid_string) == 6 and re.match(r'^[a-fA-F0-9]{6}$', uuid_string):
        return True, None
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

def validate_token(token, blacklisted_tokens):
    """Validate JWT token format"""
    if not token or not isinstance(token, str):
        return False, "Token is required and must be a string"
    
    if token in blacklisted_tokens:
        return False, "Token has been blacklisted"
    
    try:
        jwt.decode(token, get_secret('SECRET_KEY'), algorithms=["HS256"])
        return True, None
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token format"

def get_user_from_token(request):
    """Extract username from authorized token"""
    if not auth.authorized(request):
        return None
    
    if hasattr(request, 'headers'):
        token = request.headers.get('x-access-token')
    else:
        headers = request.get('headers', {})
        token = headers.get('x-access-token')
    
    if not token or not isinstance(token, str):
        return None
    
    try:
        data = auth.jwt.decode(token, get_secret('SECRET_KEY'), algorithms=["HS256"])
        username = data.get('username')
        if not username or not isinstance(username, str):
            return None
        return username
    except:
        return None
    
def get_user_credentials(username):
    """Get user credentials from BigQuery"""
    return db_get_user_credentials(username)