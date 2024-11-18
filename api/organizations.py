import os
from google.cloud import bigquery
from datetime import datetime
import uuid
import utils

project_id = os.environ.get('GCP_PROJECT')

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
    username = utils.get_user_from_token(request, utils.get_secret('SECRET_KEY'))
    if not username:
        return {"message": "Unauthorized"}, 401

    # Validate request data
    data, error = utils.validate_request_data(request)
    if error:
        return {"message": error}, 400

    org_name = data.get('organization_name')
    is_valid, error = utils.validate_organization_name(org_name)
    if not is_valid:
        return {"message": error}, 400

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
    org_id = str(uuid.uuid4()).replace('-', '')[:6]  # Shorten to 6 characters with no dashes
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
    username = utils.get_user_from_token(request, utils.get_secret('SECRET_KEY'))
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
    username = utils.get_user_from_token(request, utils.get_secret('SECRET_KEY'))
    if not username:
        return {"message": "Unauthorized"}, 401

    # Validate request data
    data, error = utils.validate_request_data(request)
    if error:
        return {"message": error}, 400

    demand_org_id = data.get('demand_org_id')
    supply_org_id = data.get('supply_org_id')
    
    # Validate organization IDs
    if not demand_org_id or not supply_org_id:
        return {"message": "Both organization IDs are required"}, 400
    
    is_valid, error = utils.validate_uuid(demand_org_id)
    if not is_valid:
        return {"message": f"Invalid demand organization ID: {error}"}, 400
    
    is_valid, error = utils.validate_uuid(supply_org_id)
    if not is_valid:
        return {"message": f"Invalid supply organization ID: {error}"}, 400

    if demand_org_id == supply_org_id:
        return {"message": "Demand and supply organizations must be different"}, 400

    client = bigquery.Client()
    
    # Verify user has access to demand organization
    query = f"""
        SELECT organization_id FROM `{project_id}.users.user_organization`
        WHERE username = '{username}' AND organization_id = '{demand_org_id}'
    """
    results = client.query(query).result()
    if not list(results):
        return {"message": "Unauthorized access to demand organization"}, 401

    # Verify both organizations exist
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_id IN ('{demand_org_id}', '{supply_org_id}')
    """
    results = list(client.query(query).result())
    if len(results) != 2:
        return {"message": "One or both organizations do not exist"}, 400

    # Check if partnership already exists
    query = f"""
        SELECT partnership_id FROM `{project_id}.organizations.partnerships`
        WHERE (demand_org_id = '{demand_org_id}' AND supply_org_id = '{supply_org_id}')
        OR (demand_org_id = '{supply_org_id}' AND supply_org_id = '{demand_org_id}')
    """
    results = client.query(query).result()
    if list(results):
        return {"message": "Partnership already exists between these organizations"}, 400

    # Create partnership
    partnership_id = str(uuid.uuid4()).replace('-', '')[:6]  # Shorten to 6 characters with no dashes
    partnership_insert = {
        'partnership_id': partnership_id,
        'demand_org_id': demand_org_id,
        'supply_org_id': supply_org_id
    }
    
    errors = client.insert_rows_json(f"{project_id}.organizations.partnerships", [partnership_insert])
    if errors:
        return {"message": "Failed to create partnership"}, 500

    return {"message": "Partnership created successfully", "partnership_id": partnership_id}, 200

def list_partnerships(request):
    """List partnerships for organizations user has access to (distinct)"""
    username = utils.get_user_from_token(request, utils.get_secret('SECRET_KEY'))
    if not username:
        return {"message": "Unauthorized"}, 401

    client = bigquery.Client()
    query = f"""
        SELECT DISTINCT
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
        JOIN `{project_id}.organizations.organizations` s ON p.supply_org_id = s.organization_id
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
            'supply_organization': {
                'organization_id': row.supply_org_id,
                'organization_name': row.supply_org_name,
                'created_by': row.supply_org_created_by,
                'created_at': row.supply_org_created_at.isoformat()
            }
        })
    
    return {"partnerships": partnerships}, 200