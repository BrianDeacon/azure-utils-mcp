import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.cosmos.exceptions import CosmosHttpResponseError

from azure_utils_mcp.client import get_container_client


def upsert_item(account: str, database: str, container: str, item: dict) -> str:
    if "id" not in item:
        return "Item must include an 'id' field."

    try:
        client = get_container_client(account, database, container)
        result = client.upsert_item(body=item)
    except CosmosHttpResponseError as e:
        return f"Cosmos DB returned an error: {e.message}"
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    return json.dumps(result, indent=2, default=str)
