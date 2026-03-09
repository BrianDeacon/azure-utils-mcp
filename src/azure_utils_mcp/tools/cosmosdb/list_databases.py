import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError

from azure_utils_mcp.client import get_cosmos_client


def list_databases(account: str) -> str:
    try:
        client = get_cosmos_client(account)
        databases = sorted(db["id"] for db in client.list_databases())
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    if not databases:
        return f"No databases found in account '{account}'."

    return json.dumps(databases, indent=2)
