import os
import re
from flask import Flask, make_response, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from google.cloud import secretmanager, bigquery
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask app
app = Flask(__name__)

# Define allowed origins
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', "http://ocl.sullhouse.com,http://localhost:5000,http://127.0.0.1:5000").split(',')

# Configure CORS with specific origins and options
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "x-access-token"]
    }
})

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
project_id = os.environ.get('GCP_PROJECT')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[os.environ.get('RATE_LIMITS', "200 per day,50 per hour")]
)

# Token blacklist
blacklisted_tokens = set()

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

def get_user_credentials(username):
    bigquery_client = bigquery.Client()
    query = f"""
        SELECT username, hashed_password
        FROM `{project_id}.users.users`
        WHERE username = '{username}'
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()

    for row in results:
        return row.username, row.hashed_password
    return None, None

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

def validate_token(token):
    """Validate JWT token format"""
    if not token or not isinstance(token, str):
        return False, "Token is required and must be a string"
    
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
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

def register(request):
    # Validate request format
    data, error = validate_request_data(request)
    if error:
        return {"message": error}, 400
    
    username = data.get('username')
    password = data.get('password')

    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        return {"message": error}, 400

    # Validate password
    is_valid, error = validate_password(password)
    if not is_valid:
        return {"message": error}, 400

    # Check if username exists
    existing_username, _ = get_user_credentials(username)
    if existing_username:
        return {"message": "Username already exists"}, 400

    # Create new user
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    client = bigquery.Client()
    table_id = f"{project_id}.users.users"
    rows_to_insert = [{"username": username, "hashed_password": hashed_password}]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    
    if errors:
        return {"message": "Failed to register user"}, 500

    return {"message": "User registered successfully"}, 201

def login(request):
    # Validate request format
    data, error = validate_request_data(request)
    if error:
        return {"message": error}, 400
    
    username = data.get('username')
    password = data.get('password')

    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        return {"message": error}, 400

    # Validate password format
    if not password or not isinstance(password, str):
        return {"message": "Password is required and must be a string"}, 400

    # Verify credentials
    stored_username, stored_hashed_password = get_user_credentials(username)
    if not stored_username or not check_password_hash(stored_hashed_password, password):
        return {"message": "Invalid credentials"}, 401

    # Generate token
    secret_key = get_secret('SECRET_KEY')
    token = jwt.encode(
        {
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        secret_key
    )
    return {"token": token}, 200

def protected(request):
    # Validate token in headers
    token = request.headers.get('x-access-token')
    is_valid, error = validate_token(token)
    if not is_valid:
        return {"message": error}, 401

    try:
        data = jwt.decode(token, get_secret('SECRET_KEY'), algorithms=["HS256"])
        current_user = data['username']
        
        # Validate extracted username
        is_valid, error = validate_username(current_user)
        if not is_valid:
            return {"message": "Invalid username in token"}, 401
            
        return {"message": f"Hello {current_user}, you are authorized to access this resource"}, 200
    except Exception as e:
        return {"message": f"Token validation error: {str(e)}"}, 401

def logout(request):
    token = request.headers.get('x-access-token')
    if token:
        blacklisted_tokens.add(token)
    response = make_response({"message": "Logged out successfully"}, 200)
    response.set_cookie('token', '', expires=0)
    return response

def authorized(request):
    """Check if the request is authenticated based on the token in headers"""
    # Get token from headers
    if hasattr(request, 'headers'):
        token = request.headers.get('x-access-token')
    else:
        headers = request.get('headers', {})
        token = headers.get('x-access-token')

    if not token:
        return False

    try:
        secret_key = get_secret('SECRET_KEY')
        jwt.decode(token, secret_key, algorithms=["HS256"])
        return True
    except Exception as e:
        print("Token decode error:", str(e))
        return False

@limiter.limit(os.environ.get('REFRESH_RATE_LIMIT', "5 per minute"))
def refresh(request):
    # Validate token in headers
    token = request.headers.get('x-access-token')
    is_valid, error = validate_token(token)
    if not is_valid:
        return {"message": error}, 401

    try:
        data = jwt.decode(token, get_secret('SECRET_KEY'), algorithms=["HS256"], options={"verify_exp": False})
        current_user = data['username']

        # Validate extracted username
        is_valid, error = validate_username(current_user)
        if not is_valid:
            return {"message": "Invalid username in token"}, 401

        # Generate new token
        new_token = jwt.encode(
            {
                'username': current_user,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            get_secret('SECRET_KEY')
        )
        return {"token": new_token}, 200
    except Exception as e:
        return {"message": f"Token refresh error: {str(e)}"}, 401

def cleanup_expired_tokens():
    """Cleanup expired tokens from the blacklist"""
    current_time = datetime.datetime.utcnow()
    expired_tokens = {token for token in blacklisted_tokens if jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"], options={"verify_exp": False})['exp'] < current_time}
    blacklisted_tokens.difference_update(expired_tokens)

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')