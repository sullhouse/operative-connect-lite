from google.cloud import bigquery
import os

project_id = os.environ.get('GCP_PROJECT')

def execute_query(query):
    client = bigquery.Client()
    query_job = client.query(query)
    return query_job.result()

def insert_rows(table_id, rows):
    client = bigquery.Client()
    errors = client.insert_rows_json(table_id, rows)
    return errors

def get_user_credentials(username):
    query = f"""
        SELECT username, hashed_password
        FROM `{project_id}.users.users`
        WHERE username = '{username}'
    """
    results = execute_query(query)
    for row in results:
        return row.username, row.hashed_password
    return None, None

def get_organization_details(org_id):
    query = f"""
        SELECT organization_id, organization_name, created_by, created_at
        FROM `{project_id}.organizations.organizations`
        WHERE organization_id = '{org_id}'
    """
    results = execute_query(query)
    for row in results:
        return {
            'organization_id': row.organization_id,
            'organization_name': row.organization_name,
            'created_by': row.created_by,
            'created_at': row.created_at.isoformat()
        }
    return None

def check_organization_name_exists(org_name):
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_name = '{org_name}'
    """
    results = execute_query(query)
    return list(results)

def check_user_access_to_organization(username, org_id):
    query = f"""
        SELECT organization_id FROM `{project_id}.users.user_organization`
        WHERE username = '{username}' AND organization_id = '{org_id}'
    """
    results = execute_query(query)
    return list(results)

def check_organizations_exist(org_ids):
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_id IN ({','.join(f"'{org_id}'" for org_id in org_ids)})
    """
    results = execute_query(query)
    return list(results)

def check_partnership_exists(demand_org_id, supply_org_id):
    query = f"""
        SELECT partnership_id FROM `{project_id}.organizations.partnerships`
        WHERE (demand_org_id = '{demand_org_id}' AND supply_org_id = '{supply_org_id}')
        OR (demand_org_id = '{supply_org_id}' AND supply_org_id = '{demand_org_id}')
    """
    results = execute_query(query)
    return list(results)

def list_organizations_for_user(username):
    query = f"""
        SELECT o.* 
        FROM `{project_id}.organizations.organizations` o
        JOIN `{project_id}.users.user_organization` uo 
        ON o.organization_id = uo.organization_id
        WHERE uo.username = '{username}'
    """
    return execute_query(query)

def list_partnerships_for_user(username):
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
    return execute_query(query)

def get_organization_id_by_name(org_name):
    query = f"""
        SELECT organization_id FROM `{project_id}.organizations.organizations`
        WHERE organization_name = '{org_name}'
    """
    results = execute_query(query)
    for row in results:
        return row.organization_id
    return None