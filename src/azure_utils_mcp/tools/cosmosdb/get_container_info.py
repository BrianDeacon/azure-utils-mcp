import json

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError

from azure_utils_mcp.client import get_database_client


def get_container_info(account: str, database: str, container: str) -> str:
    try:
        db = get_database_client(account, database)
        props = db.get_container_client(container).read()
    except CosmosResourceNotFoundError:
        return f"Container '{container}' not found in database '{database}'."
    except CosmosHttpResponseError as e:
        return f"Cosmos DB returned an error: {e.message}"
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except ServiceRequestError as e:
        return f"Could not connect to Cosmos DB account '{account}': {e}"

    info = {
        "id": props.get("id"),
        "partition_key": props.get("partitionKey"),
        "indexing_policy": props.get("indexingPolicy"),
        "default_ttl": props.get("defaultTtl"),
        "unique_key_policy": props.get("uniqueKeyPolicy"),
        "_self": props.get("_self"),
        "_etag": props.get("_etag"),
        "_ts": props.get("_ts"),
    }

    return json.dumps(info, indent=2, default=str)
