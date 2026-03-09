import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.cosmos.exceptions import CosmosHttpResponseError

from azure_utils_mcp.client import get_container_client


def count_items(account: str, database: str, container: str, where: str | None = None) -> str:
    if where:
        query = f"SELECT VALUE COUNT(1) FROM c WHERE {where}"
    else:
        query = "SELECT VALUE COUNT(1) FROM c"

    try:
        client = get_container_client(account, database, container)
        results = list(client.query_items(query=query, enable_cross_partition_query=True))
    except CosmosHttpResponseError as e:
        return f"Cosmos DB returned an error: {e.message}"
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    count = results[0] if results else 0
    return json.dumps({"count": count})
