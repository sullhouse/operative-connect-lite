import os
from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from google.cloud import secretmanager
from google.cloud import bigquery

# Initialize the Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://ocl.sullhouse.com"}})
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# In-memory user storage
users = {}
project_id = os.environ.get('GCP_PROJECT')

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

def get_request_data(request_obj):
    """Helper function to get JSON data from either Flask request or dict-like object"""
    if hasattr(request_obj, 'get_json'):
        return request_obj.get_json()
    elif isinstance(request_obj, dict):
        return request_obj.get('body', {})
    return {}

def register(request):
    data = get_request_data(request)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"message": "Username and password are required"}, 400

    existing_username, _ = get_user_credentials(username)
    if existing_username:
        return {"message": "Username already exists"}, 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    client = bigquery.Client()
    table_id = f"{project_id}.users.users"
    rows_to_insert = [{"username": username, "hashed_password": hashed_password}]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        return {"message": "Failed to register user"}, 500

    return {"message": "User registered successfully"}, 200

def login(request):
    data = get_request_data(request)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {"message": "Username and password are required"}, 400

    stored_username, stored_hashed_password = get_user_credentials(username)
    if not stored_username or not check_password_hash(stored_hashed_password, password):
        return {"message": "Invalid credentials"}, 401

    secret_key = get_secret('SECRET_KEY')
    token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, secret_key)
    return {"token": token}, 200

def protected(request):
    # Debug request headers
    print("Request headers:", request.headers if hasattr(request, 'headers') else request.get('headers', {}))
    
    # Get token from headers
    if hasattr(request, 'headers'):
        token = request.headers.get('x-access-token')
    else:
        headers = request.get('headers', {})
        token = headers.get('x-access-token')

    if not token:
        return {"message": "Token is missing"}, 401

    try:
        secret_key = get_secret('SECRET_KEY')
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
        current_user = data['username']
    except Exception as e:
        print("Token decode error:", str(e))
        return {"message": "Token is invalid"}, 401

    return {"message": f"Hello {current_user}, you are authorized to access this resource"}, 200

def logout(request):
    response = make_response({"message": "Logged out successfully"}, 200)
    response.set_cookie('token', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(debug=True)