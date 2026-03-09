import json

from azure.core.exceptions import HttpResponseError
from azure.mgmt.authorization import AuthorizationManagementClient

from azure_utils_mcp.client import credential, get_subscriptions


def list_eligible_roles() -> str:
    try:
        subscriptions = get_subscriptions()
    except RuntimeError as e:
        return str(e)

    results = []
    for sub in subscriptions:
        try:
            client = AuthorizationManagementClient(credential, sub["id"])
            scope = f"/subscriptions/{sub['id']}"
            instances = list(
                client.role_eligibility_schedule_instances.list_for_scope(
                    scope=scope,
                    filter="asTarget()",
                )
            )
            for i in instances:
                try:
                    role_name = client.role_definitions.get_by_id(i.role_definition_id).role_name
                except Exception:
                    role_name = i.role_definition_id.split("/")[-1]

                results.append({
                    "subscription": sub["name"],
                    "role": role_name,
                    "scope": i.scope,
                    "status": i.status,
                    "eligible_from": i.start_date_time.isoformat() if i.start_date_time else None,
                    "eligible_until": i.end_date_time.isoformat() if i.end_date_time else "permanent",
                })
        except HttpResponseError:
            pass
        except Exception:
            pass

    if not results:
        return "No eligible PIM roles found across accessible subscriptions."

    return json.dumps(results, indent=2)
