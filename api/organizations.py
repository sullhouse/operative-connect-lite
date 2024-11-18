import os
from google.cloud import bigquery
from datetime import datetime
import uuid
import utils
import database

project_id = os.environ.get('GCP_PROJECT')

def get_organization_details(org_id):
    """Get organization details from BigQuery"""
    return database.get_organization_details(org_id)

def create_organization(request):
    """Create a new organization and map user to it"""
    username = utils.get_user_from_token(request)
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
    if database.check_organization_name_exists(org_name):
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
    
    errors = database.insert_rows(f"{project_id}.organizations.organizations", [org_insert])
    if errors:
        return {"message": "Failed to create organization"}, 500

    # Map user to organization
    user_org_insert = {
        'username': username,
        'organization_id': org_id,
        'status': 'active'
    }
    
    errors = database.insert_rows(f"{project_id}.users.user_organization", [user_org_insert])
    if errors:
        return {"message": "Failed to map user to organization"}, 500

    return {"message": "Organization created successfully", "organization_id": org_id}, 200

def list_organizations(request):
    username = utils.get_user_from_token(request)
    if not username:
        return {"message": "Unauthorized"}, 401

    client = bigquery.Client()
    results = database.list_organizations_for_user(username)
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
    username = utils.get_user_from_token(request)
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
    if not database.check_user_access_to_organization(username, demand_org_id):
        return {"message": "Unauthorized access to demand organization"}, 401

    # Verify both organizations exist
    if len(database.check_organizations_exist([demand_org_id, supply_org_id])) != 2:
        return {"message": "One or both organizations do not exist"}, 400

    # Check if partnership already exists
    if database.check_partnership_exists(demand_org_id, supply_org_id):
        return {"message": "Partnership already exists between these organizations"}, 400

    # Create partnership
    partnership_id = str(uuid.uuid4()).replace('-', '')[:6]  # Shorten to 6 characters with no dashes
    partnership_insert = {
        'partnership_id': partnership_id,
        'demand_org_id': demand_org_id,
        'supply_org_id': supply_org_id
    }
    
    errors = database.insert_rows(f"{project_id}.organizations.partnerships", [partnership_insert])
    if errors:
        return {"message": "Failed to create partnership"}, 500

    return {"message": "Partnership created successfully", "partnership_id": partnership_id}, 200

def list_partnerships(request):
    """List partnerships for organizations user has access to (distinct)"""
    username = utils.get_user_from_token(request)
    if not username:
        return {"message": "Unauthorized"}, 401

    client = bigquery.Client()
    results = database.list_partnerships_for_user(username)
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

def map_user_to_organization(request):
    """Map a user to an existing organization"""
    username = utils.get_user_from_token(request)
    if not username:
        return {"message": "Unauthorized"}, 401

    # Validate request data
    data, error = utils.validate_request_data(request)
    if error:
        return {"message": error}, 400

    org_id = data.get('organization_id')
    if not org_id:
        return {"message": "Organization ID is required"}, 400

    client = bigquery.Client()

    # Check if organization exists
    if not database.check_organizations_exist([org_id]):
        return {"message": "Organization does not exist"}, 400

    # Map user to organization
    user_org_insert = {
        'username': username,
        'organization_id': org_id,
        'status': 'active'
    }
    
    errors = database.insert_rows(f"{project_id}.users.user_organization", [user_org_insert])
    if errors:
        return {"message": "Failed to map user to organization"}, 500

    return {"message": "User mapped to organization successfully"}, 200