import json
import re
import uuid

from azure.core.exceptions import HttpResponseError
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import (
    RoleAssignmentScheduleRequest,
    RoleAssignmentScheduleRequestPropertiesScheduleInfo,
    RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration,
)

from azure_utils_mcp.client import credential, get_principal_id, get_subscriptions


def _iso8601_to_seconds(duration: str) -> int:
    days = re.search(r"(\d+)D", duration, re.IGNORECASE)
    hours = re.search(r"(\d+)H", duration, re.IGNORECASE)
    minutes = re.search(r"T.*?(\d+)M", duration, re.IGNORECASE)
    seconds = re.search(r"(\d+)S", duration, re.IGNORECASE)
    return (
        int(days.group(1)) * 86400 if days else 0
        + int(hours.group(1)) * 3600 if hours else 0
        + int(minutes.group(1)) * 60 if minutes else 0
        + int(seconds.group(1)) if seconds else 0
    )


def _seconds_to_iso8601(seconds: int) -> str:
    if seconds % 3600 == 0:
        return f"PT{seconds // 3600}H"
    if seconds % 60 == 0:
        return f"PT{seconds // 60}M"
    return f"PT{seconds}S"


def _get_max_activation_duration(client: AuthorizationManagementClient, scope: str, role_def_id: str) -> str | None:
    try:
        assignments = list(client.role_management_policy_assignments.list_for_scope(scope=scope))
        assignment = next((a for a in assignments if a.role_definition_id == role_def_id), None)
        if not assignment:
            return None
        policy_name = assignment.policy_id.split("/")[-1]
        policy = client.role_management_policies.get(scope=scope, role_management_policy_name=policy_name)
        for rule in (policy.rules or []):
            if rule.id == "Expiration_EndUser_Assignment":
                return rule.maximum_duration
    except Exception:
        pass
    return None


def activate_role(
    role: str,
    scope: str,
    justification: str,
    duration: str | None = None,
) -> str:
    try:
        principal_id = get_principal_id()
        subscriptions = get_subscriptions()
    except RuntimeError as e:
        return str(e)

    sub_id = None
    for sub in subscriptions:
        if f"/subscriptions/{sub['id']}" in scope:
            sub_id = sub["id"]
            break

    if not sub_id:
        return f"Could not match scope '{scope}' to an accessible subscription."

    client = AuthorizationManagementClient(credential, sub_id)

    role_def_id = None
    try:
        for rd in client.role_definitions.list(scope=scope):
            if rd.role_name.lower() == role.lower():
                role_def_id = rd.id
                break
    except HttpResponseError as e:
        return f"Azure returned an error looking up role definitions: {e.message}"

    if not role_def_id:
        return f"Role '{role}' not found at scope '{scope}'."

    try:
        eligibilities = list(
            client.role_eligibility_schedule_instances.list_for_scope(
                scope=scope,
                filter=f"asTarget() and roleDefinitionId eq '{role_def_id}'",
            )
        )
    except HttpResponseError as e:
        return f"Azure returned an error checking eligibility: {e.message}"

    if not eligibilities:
        return f"You are not eligible to activate '{role}' at scope '{scope}'."

    max_duration = _get_max_activation_duration(client, scope, role_def_id)

    if duration is None:
        if max_duration:
            duration = max_duration
        else:
            duration = "PT8H"
    elif max_duration and _iso8601_to_seconds(duration) > _iso8601_to_seconds(max_duration):
        duration = max_duration

    try:
        result = client.role_assignment_schedule_requests.create(
            scope=scope,
            role_assignment_schedule_request_name=str(uuid.uuid4()),
            parameters=RoleAssignmentScheduleRequest(
                principal_id=principal_id,
                role_definition_id=role_def_id,
                request_type="SelfActivate",
                justification=justification,
                schedule_info=RoleAssignmentScheduleRequestPropertiesScheduleInfo(
                    expiration=RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration(
                        type="AfterDuration",
                        duration=duration,
                    )
                ),
            ),
        )
    except HttpResponseError as e:
        return f"Azure returned an error activating the role: {e.message}"

    return json.dumps({
        "status": result.status,
        "role": role,
        "scope": scope,
        "duration": duration,
        "request_id": result.name,
    }, indent=2)
