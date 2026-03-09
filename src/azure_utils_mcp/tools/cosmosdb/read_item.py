import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError

from azure_utils_mcp.client import get_container_client


def read_item(account: str, database: str, container: str, item_id: str, partition_key: str) -> str:
    try:
        client = get_container_client(account, database, container)
        item = client.read_item(item=item_id, partition_key=partition_key)
    except CosmosResourceNotFoundError:
        return f"Item '{item_id}' not found in container '{container}'."
    except CosmosHttpResponseError as e:
        return f"Cosmos DB returned an error: {e.message}"
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    return json.dumps(item, indent=2, default=str)
