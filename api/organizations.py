import os
from google.cloud import bigquery
from datetime import datetime
import uuid
import auth
import re

project_id = os.environ.get('GCP_PROJECT')

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

def validate_request_data(request):
    """Validate request data format"""
    if hasattr(request, 'get_json'):
        data = request.get_json()
    else:
        data = request.get('body', {})
    
    if not isinstance(data, dict):
        return None, "Invalid request data format"
    
    return data, None

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
        secret_key = auth.get_secret('SECRET_KEY')
        data = auth.jwt.decode(token, secret_key, algorithms=["HS256"])
        username = data.get('username')
        if not username or not isinstance(username, str):
            return None
        return username
    except:
        return None

def get_organization_details(org_id):
    """Get organization details from BigQuery"""
    client = bigquery.Client()
    query = f"""
        SELECT organization_id, organization_name, created_by, created_at
        FROM `{project_id}.organizations.organizations`
        WHERE organization_id = '{org_id}'
    """
    query_job = client.query(query)
    results = query_job.result()
    
    for row in results:
        return {
            'organization_id': row.organization_id,
            'organization_name': row.organization_name,
            'created_by': row.created_by,
            'created_at': row.created_at.isoformat()
        }
    return None

def create_organization(request):
    """Create a new organization and map user to it"""
    username = get_user_from_token(request)
    if not username:
        return {"error": {"code": "UNAUTHORIZED", "message": "Unauthorized"}}, 401

    # Validate request data
    data, error = validate_request_data(request)
    if error:
        return {"error": {"code": "INVALID_REQUEST", "message": error}}, 400

    org_name = data.get('organization_name')
    is_valid, error = validate_organization_name(org_name)
    if not is_valid:
        return {"error": {"code": "INVALID_ORGANIZATION_NAME", "message": error}}, 400

    client = bigquery.Client()
    
    # Check if organization name exists
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_name = '{org_name}'
    """
    results = client.query(query).result()
    if list(results):
        return {"error": {"code": "ORGANIZATION_EXISTS", "message": "Organization name already exists"}}, 400

    # Create organization
    org_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    org_insert = {
        'organization_id': org_id,
        'organization_name': org_name,
        'created_by': username,
        'created_at': created_at.isoformat()
    }
    
    errors = client.insert_rows_json(f"{project_id}.organizations.organizations", [org_insert])
    if errors:
        return {"error": {"code": "INTERNAL_ERROR", "message": "Failed to create organization"}}, 500

    # Map user to organization
    user_org_insert = {
        'username': username,
        'organization_id': org_id,
        'status': 'active'
    }
    
    errors = client.insert_rows_json(f"{project_id}.users.user_organization", [user_org_insert])
    if errors:
        return {"error": {"code": "INTERNAL_ERROR", "message": "Failed to map user to organization"}}, 500

    return {"message": "Organization created successfully", "organization_id": org_id}, 200

def list_organizations(request):
    """List organizations user has access to"""
    username = get_user_from_token(request)
    if not username:
        return {"message": "Unauthorized"}, 401

    client = bigquery.Client()
    query = f"""
        SELECT o.* 
        FROM `{project_id}.organizations.organizations` o
        JOIN `{project_id}.users.user_organization` uo 
        ON o.organization_id = uo.organization_id
        WHERE uo.username = '{username}'
    """
    
    results = client.query(query).result()
    organizations = []
    for row in results:
        organizations.append({
            'organization_id': row.organization_id,
            'organization_name': row.organization_name,
            'created_by': row.created_by,
            'created_at': row.created_at.isoformat()
        })
    
    return {"organizations": organizations}, 200

def create_partnership(request):
    """Create partnership between two organizations"""
    username = get_user_from_token(request)
    if not username:
        return {"error": {"code": "UNAUTHORIZED", "message": "Unauthorized"}}, 401

    # Validate request data
    data, error = validate_request_data(request)
    if error:
        return {"error": {"code": "INVALID_REQUEST", "message": error}}, 400

    demand_org_id = data.get('demand_org_id')
    supply_org_id = data.get('supply_org_id')
    
    # Validate organization IDs
    if not demand_org_id or not supply_org_id:
        return {"error": {"code": "INVALID_ORGANIZATION_ID", "message": "Both organization IDs are required"}}, 400
    
    is_valid, error = validate_uuid(demand_org_id)
    if not is_valid:
        return {"error": {"code": "INVALID_UUID", "message": f"Invalid demand organization ID: {error}"}}, 400
    
    is_valid, error = validate_uuid(supply_org_id)
    if not is_valid:
        return {"error": {"code": "INVALID_UUID", "message": f"Invalid supply organization ID: {error}"}}, 400

    if demand_org_id == supply_org_id:
        return {"error": {"code": "INVALID_ORGANIZATION_ID", "message": "Demand and supply organizations must be different"}}, 400

    client = bigquery.Client()
    
    # Verify user has access to demand organization
    query = f"""
        SELECT organization_id FROM `{project_id}.users.user_organization`
        WHERE username = '{username}' AND organization_id = '{demand_org_id}'
    """
    results = client.query(query).result()
    if not list(results):
        return {"error": {"code": "UNAUTHORIZED", "message": "Unauthorized access to demand organization"}}, 401

    # Verify both organizations exist
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_id IN ('{demand_org_id}', '{supply_org_id}')
    """
    results = list(client.query(query).result())
    if len(results) != 2:
        return {"error": {"code": "ORGANIZATION_NOT_FOUND", "message": "One or both organizations do not exist"}}, 400

    # Check if partnership already exists
    query = f"""
        SELECT partnership_id FROM `{project_id}.organizations.partnerships`
        WHERE (demand_org_id = '{demand_org_id}' AND supply_org_id = '{supply_org_id}')
        OR (demand_org_id = '{supply_org_id}' AND supply_org_id = '{demand_org_id}')
    """
    results = client.query(query).result()
    if list(results):
        return {"error": {"code": "PARTNERSHIP_EXISTS", "message": "Partnership already exists between these organizations"}}, 400

    # Create partnership
    partnership_id = str(uuid.uuid4())
    partnership_insert = {
        'partnership_id': partnership_id,
        'demand_org_id': demand_org_id,
        'supply_org_id': supply_org_id
    }
    
    errors = client.insert_rows_json(f"{project_id}.organizations.partnerships", [partnership_insert])
    if errors:
        return {"error": {"code": "INTERNAL_ERROR", "message": "Failed to create partnership"}}, 500

    return {"message": "Partnership created successfully", "partnership_id": partnership_id}, 200

def list_partnerships(request):
    """List partnerships for organizations user has access to"""
    username = get_user_from_token(request)
    if not username:
        return {"message": "Unauthorized"}, 401

    client = bigquery.Client()
    query = f"""
        SELECT 
            p.partnership_id,
            d.organization_id as demand_org_id,
            d.organization_name as demand_org_name,
            d.created_by as demand_org_created_by,
            d.created_at as demand_org_created_at,
            s.organization_id as supply_org_id,
            s.organization_name as supply_org_name,
            s.created_by as supply_org_created_by,
            s.created_at as supply_org_created_at
        FROM `{project_id}.organizations.partnerships` p
        JOIN `{project_id}.organizations.organizations` d ON p.demand_org_id = d.organization_id
        JOIN `{project_id}.organizations.organizations` s ON p.supply_org_id = s.organization_id  # Updated join condition
        JOIN `{project_id}.users.user_organization` uo 
        ON uo.organization_id = d.organization_id OR uo.organization_id = s.organization_id
        WHERE uo.username = '{username}'
    """
    
    results = client.query(query).result()
    partnerships = []
    for row in results:
        partnerships.append({
            'partnership_id': row.partnership_id,
            'demand_organization': {
                'organization_id': row.demand_org_id,
                'organization_name': row.demand_org_name,
                'created_by': row.demand_org_created_by,
                'created_at': row.demand_org_created_at.isoformat()
            },
            'supply_organization': {  # Updated key name
                'organization_id': row.supply_org_id,  # Updated field name
                'organization_name': row.supply_org_name,
                'created_by': row.supply_org_created_by,
                'created_at': row.supply_org_created_at.isoformat()
            }
        })
    
    return {"partnerships": partnerships}, 200