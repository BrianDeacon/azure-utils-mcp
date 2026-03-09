import json

from azure.core.exceptions import HttpResponseError

from azure_utils_mcp.client import get_cosmos_mgmt_client


def list_accounts() -> str:
    try:
        client = get_cosmos_mgmt_client()
        accounts = sorted(a.name for a in client.database_accounts.list())
    except HttpResponseError as e:
        return f"Azure returned an error: {e.message}"
    except RuntimeError as e:
        return str(e)

    if not accounts:
        return "No Cosmos DB accounts found in the current subscription."

    return json.dumps(accounts, indent=2)
