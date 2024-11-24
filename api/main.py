import functions_framework
from flask import Response, Flask, request
from flask_cors import CORS
from google.cloud import storage
import json
import datetime
import uuid
import os

app = Flask(__name__)

# Define allowed origins
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 
    'http://ocl.sullhouse.com,http://localhost:8000,http://127.0.0.1:8000'
).split(',')

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "x-access-token"],
        "supports_credentials": True
    }
})

def handle_request(request):
    """Main handler function that can be called either by Flask route or Cloud Function"""
    # Handle preflight OPTIONS requests
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,x-access-token')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Get a reference to the GCS bucket and folder
    bucket_name = "operative-connect-lite"
    folder_name = "requests"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    try:
        # Generate a timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        short_uuid = str(uuid.uuid4())[:8]

        # Create a filename with the timestamp
        filename = f"request_{timestamp}_{short_uuid}.json"

        # Construct the full path within the bucket
        blob = bucket.blob(f"{folder_name}/{filename}")

        # Create a dictionary to hold the entire request data
        request_data = {
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'body': request.get_json() if request.is_json else None
        }

        # Save the request data to the GCS bucket
        blob.upload_from_string(
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # Get the function name from the request URL
        function_name = request.path.lstrip("/").split("?")[0]

        # Define a dictionary mapping function names to modules
        functions = {
            "auth/register": "auth.register", 
            "auth/login": "auth.login",
            "auth/protected": "auth.protected",
            "auth/refresh": "auth.refresh",
            "organizations/create": "organizations.create_organization",
            "organizations/list": "organizations.list_organizations",
            "organizations/partnerships/create": "organizations.create_partnership",
            "organizations/partnerships/list": "organizations.list_partnerships",
            "organizations/map_user": "organizations.map_user_to_organization"
        }

        # Import the corresponding module dynamically
        if function_name in functions:
            module_name, function_name = functions[function_name].rsplit(".", 1)
            imported_module = __import__(module_name)
            function = getattr(imported_module, function_name)
            # Call the function with the request
            response, status_code = function(request)

            folder_name = "responses"

            try:
                filename = f"response_{timestamp}_{short_uuid}.json"
                blob = bucket.blob(f"{folder_name}/{filename}")
                response_data = {
                    "status_code": status_code,
                    "data": response
                }
                blob.upload_from_string(
                    data=json.dumps(response_data),
                    content_type='application/json'
                )
            except Exception as e:
                error_response = Response(json.dumps({"error": {"code": "INTERNAL_ERROR", "message": str(e)}}), status=500, mimetype='application/json')
                return error_response

            json_response = Response(json.dumps(response), status=status_code, mimetype='application/json')
            return json_response
        else:
            error_response = Response(json.dumps({"error": {"code": "NOT_FOUND", "message": "Function not found"}}), status=404, mimetype='application/json')
            return error_response

    except Exception as e:
        error_response = Response(json.dumps({"error": {"code": "INTERNAL_ERROR", "message": str(e)}}), status=500, mimetype='application/json')
        return error_response

# Cloud Function entry point
@functions_framework.http
def hello_http(request):
    """Cloud Function entry point"""
    return handle_request(request)

# Flask route for local development
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def flask_handler(path):
    """Flask route handler for local development"""
    return handle_request(request)

if __name__ == '__main__':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'operative-connect-lite-41ee5442dc06.json'
    app.run(host='127.0.0.1', port=5000, debug=True)

