import base64
import json
import os

from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy
from azure.identity import DefaultAzureCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.servicebus import ServiceBusClient as _ServiceBusClient
from azure.servicebus.management import ServiceBusAdministrationClient

credential = DefaultAzureCredential()

_cosmos_clients: dict[str, CosmosClient] = {}
_db_clients: dict[tuple[str, str], DatabaseProxy] = {}
_container_clients: dict[tuple[str, str, str], ContainerProxy] = {}
_cosmos_mgmt_client: CosmosDBManagementClient | None = None
_servicebus_clients: dict[str, _ServiceBusClient] = {}
_servicebus_admin_clients: dict[str, ServiceBusAdministrationClient] = {}
_servicebus_mgmt_client: ServiceBusManagementClient | None = None
_subscription_id: str | None = None
_subscriptions: list[dict] | None = None
_principal_id: str | None = None


def _normalize_cosmos_endpoint(account: str) -> str:
    if account.startswith("https://"):
        return account.rstrip("/")
    return f"https://{account}.documents.azure.com"


def _normalize_servicebus_namespace(namespace: str) -> str:
    if not namespace.endswith(".servicebus.windows.net"):
        return f"{namespace}.servicebus.windows.net"
    return namespace


def get_subscriptions() -> list[dict]:
    global _subscriptions
    if _subscriptions is None:
        sub_client = SubscriptionClient(credential)
        _subscriptions = [
            {"name": s.display_name, "id": s.subscription_id}
            for s in sub_client.subscriptions.list()
            if s.state == "Enabled"
        ]
    return _subscriptions


def get_subscription_id() -> str:
    global _subscription_id
    if _subscription_id:
        return _subscription_id

    from_env = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if from_env:
        _subscription_id = from_env
        return _subscription_id

    subs = get_subscriptions()
    if len(subs) == 1:
        _subscription_id = subs[0]["id"]
        return _subscription_id

    raise RuntimeError(
        "Multiple subscriptions found. Set AZURE_SUBSCRIPTION_ID to specify which one to use."
    )


def get_principal_id() -> str:
    global _principal_id
    if _principal_id:
        return _principal_id

    token = credential.get_token("https://management.azure.com/.default").token
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.b64decode(payload))
    _principal_id = claims.get("oid") or claims.get("appid")

    if not _principal_id:
        raise RuntimeError("Could not determine principal ID from credential token.")

    return _principal_id


def get_cosmos_client(account: str) -> CosmosClient:
    endpoint = _normalize_cosmos_endpoint(account)
    if endpoint not in _cosmos_clients:
        key = os.environ.get("AZURE_COSMOS_KEY")
        if key:
            _cosmos_clients[endpoint] = CosmosClient(url=endpoint, credential=key)
        else:
            _cosmos_clients[endpoint] = CosmosClient(url=endpoint, credential=credential)
    return _cosmos_clients[endpoint]


def get_database_client(account: str, database: str) -> DatabaseProxy:
    key = (_normalize_cosmos_endpoint(account), database)
    if key not in _db_clients:
        _db_clients[key] = get_cosmos_client(account).get_database_client(database)
    return _db_clients[key]


def get_container_client(account: str, database: str, container: str) -> ContainerProxy:
    key = (_normalize_cosmos_endpoint(account), database, container)
    if key not in _container_clients:
        _container_clients[key] = get_database_client(account, database).get_container_client(container)
    return _container_clients[key]


def get_cosmos_mgmt_client() -> CosmosDBManagementClient:
    global _cosmos_mgmt_client
    if _cosmos_mgmt_client is None:
        _cosmos_mgmt_client = CosmosDBManagementClient(
            credential=credential,
            subscription_id=get_subscription_id(),
        )
    return _cosmos_mgmt_client


def get_servicebus_client(namespace: str) -> _ServiceBusClient:
    namespace = _normalize_servicebus_namespace(namespace)
    if namespace not in _servicebus_clients:
        conn_str = os.environ.get("AZURE_SERVICEBUS_CONNECTION_STRING")
        if conn_str:
            _servicebus_clients[namespace] = _ServiceBusClient.from_connection_string(conn_str)
        else:
            _servicebus_clients[namespace] = _ServiceBusClient(
                fully_qualified_namespace=namespace,
                credential=credential,
            )
    return _servicebus_clients[namespace]


def get_servicebus_admin_client(namespace: str) -> ServiceBusAdministrationClient:
    namespace = _normalize_servicebus_namespace(namespace)
    if namespace not in _servicebus_admin_clients:
        conn_str = os.environ.get("AZURE_SERVICEBUS_CONNECTION_STRING")
        if conn_str:
            _servicebus_admin_clients[namespace] = ServiceBusAdministrationClient.from_connection_string(conn_str)
        else:
            _servicebus_admin_clients[namespace] = ServiceBusAdministrationClient(
                fully_qualified_namespace=namespace,
                credential=credential,
            )
    return _servicebus_admin_clients[namespace]


def get_servicebus_mgmt_client() -> ServiceBusManagementClient:
    global _servicebus_mgmt_client
    if _servicebus_mgmt_client is None:
        _servicebus_mgmt_client = ServiceBusManagementClient(
            credential=credential,
            subscription_id=get_subscription_id(),
        )
    return _servicebus_mgmt_client
