import json
from pathlib import Path

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.cosmos.exceptions import CosmosHttpResponseError

from azure_utils_mcp.client import get_container_client


def query_items(
    account: str,
    database: str,
    container: str,
    query: str,
    max_items: int = 100,
    save_to: str | None = None,
) -> str:
    if max_items > 1000:
        max_items = 1000

    try:
        client = get_container_client(account, database, container)
        items = list(client.query_items(query=query, max_item_count=max_items, enable_cross_partition_query=True))
        if len(items) > max_items:
            items = items[:max_items]
    except CosmosHttpResponseError as e:
        return f"Cosmos DB returned an error: {e.message}"
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    if not items:
        return f"No items matched the query in '{container}'."

    if save_to:
        Path(save_to).write_text(json.dumps(items, indent=2, default=str))
        return f"{len(items)} item(s) saved to {save_to}."

    return json.dumps(items, indent=2, default=str)
