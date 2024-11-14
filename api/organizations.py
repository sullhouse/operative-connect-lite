import os
from google.cloud import bigquery
from datetime import datetime
import uuid
import auth

project_id = os.environ.get('GCP_PROJECT')

def get_user_from_token(request):
    """Extract username from authorized token"""
    if not auth.authorized(request):
        return None
    
    if hasattr(request, 'headers'):
        token = request.headers.get('x-access-token')
    else:
        headers = request.get('headers', {})
        token = headers.get('x-access-token')
    
    secret_key = auth.get_secret('SECRET_KEY')
    data = auth.jwt.decode(token, secret_key, algorithms=["HS256"])
    return data['username']

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
        return {"message": "Unauthorized"}, 401

    data = request.get_json() if hasattr(request, 'get_json') else request.get('body', {})
    org_name = data.get('organization_name')
    
    if not org_name:
        return {"message": "Organization name is required"}, 400

    client = bigquery.Client()
    
    # Check if organization name exists
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_name = '{org_name}'
    """
    results = client.query(query).result()
    if list(results):
        return {"message": "Organization name already exists"}, 400

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
        return {"message": "Failed to create organization"}, 500

    # Map user to organization
    user_org_insert = {
        'username': username,
        'organization_id': org_id,
        'status': 'active'
    }
    
    errors = client.insert_rows_json(f"{project_id}.users.user_organization", [user_org_insert])
    if errors:
        return {"message": "Failed to map user to organization"}, 500

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
        return {"message": "Unauthorized"}, 401

    data = request.get_json() if hasattr(request, 'get_json') else request.get('body', {})
    demand_org_id = data.get('demand_org_id')
    supply_org_id = data.get('supply_org_id')  # Updated parameter name
    
    if not demand_org_id or not supply_org_id:  # Updated check
        return {"message": "Both organization IDs are required"}, 400

    client = bigquery.Client()
    
    # Verify user has access to demand organization
    query = f"""
        SELECT organization_id FROM `{project_id}.users.user_organization`
        WHERE username = '{username}' AND organization_id = '{demand_org_id}'
    """
    results = client.query(query).result()
    if not list(results):
        return {"message": "Unauthorized access to demand organization"}, 401

    # Create partnership
    partnership_id = str(uuid.uuid4())
    partnership_insert = {
        'partnership_id': partnership_id,
        'demand_org_id': demand_org_id,
        'supply_org_id': supply_org_id  # Updated field name
    }
    
    errors = client.insert_rows_json(f"{project_id}.organizations.partnerships", [partnership_insert])
    if errors:
        return {"message": "Failed to create partnership"}, 500

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