import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError

from azure_utils_mcp.client import get_database_client


def list_containers(account: str, database: str) -> str:
    try:
        db = get_database_client(account, database)
        containers = sorted(c["id"] for c in db.list_containers())
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    if not containers:
        return f"No containers found in database '{database}'."

    return json.dumps(containers, indent=2)
