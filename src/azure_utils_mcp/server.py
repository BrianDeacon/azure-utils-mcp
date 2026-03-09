from mcp.server.fastmcp import FastMCP

from azure_utils_mcp.tools.authorization.activate_role import activate_role
from azure_utils_mcp.tools.authorization.list_eligible_roles import list_eligible_roles
from azure_utils_mcp.tools.cosmosdb.count_items import count_items
from azure_utils_mcp.tools.cosmosdb.delete_item import delete_item
from azure_utils_mcp.tools.cosmosdb.get_container_info import get_container_info
from azure_utils_mcp.tools.cosmosdb.list_accounts import list_accounts
from azure_utils_mcp.tools.cosmosdb.list_containers import list_containers
from azure_utils_mcp.tools.cosmosdb.list_databases import list_databases
from azure_utils_mcp.tools.cosmosdb.query_items import query_items
from azure_utils_mcp.tools.cosmosdb.read_item import read_item
from azure_utils_mcp.tools.cosmosdb.upsert_item import upsert_item
from azure_utils_mcp.tools.servicebus.list_namespaces import list_namespaces
from azure_utils_mcp.tools.servicebus.list_queues import list_queues
from azure_utils_mcp.tools.servicebus.list_topics import list_topics
from azure_utils_mcp.tools.servicebus.peek_dlq import peek_dlq
from azure_utils_mcp.tools.servicebus.peek_messages import peek_messages
from azure_utils_mcp.tools.servicebus.peek_subscription_dlq import peek_subscription_dlq
from azure_utils_mcp.tools.servicebus.peek_subscription_messages import peek_subscription_messages
from azure_utils_mcp.tools.servicebus.purge_dlq import purge_dlq
from azure_utils_mcp.tools.servicebus.purge_queue import purge_queue
from azure_utils_mcp.tools.servicebus.purge_subscription import purge_subscription
from azure_utils_mcp.tools.servicebus.purge_subscription_dlq import purge_subscription_dlq
from azure_utils_mcp.tools.servicebus.requeue_dlq import requeue_dlq
from azure_utils_mcp.tools.servicebus.requeue_subscription_dlq import requeue_subscription_dlq
from azure_utils_mcp.tools.servicebus.send_batch import send_batch
from azure_utils_mcp.tools.servicebus.send_message import send_message

app = FastMCP("azure-utils-mcp")


# ── Cosmos DB ────────────────────────────────────────────────────────────────

@app.tool()
def cosmosdb_list_accounts() -> str:
    """List all Azure Cosmos DB accounts in the current subscription.

    The subscription is resolved automatically — first from the AZURE_SUBSCRIPTION_ID
    environment variable, then from the active 'az login' session. If neither is
    available, an error is returned with instructions.
    """
    return list_accounts()


@app.tool()
def cosmosdb_list_databases(account: str) -> str:
    """List all databases in an Azure Cosmos DB account.

    Returns a sorted JSON array of database names.
    The account can be given as a short name (e.g. my-cosmos-account)
    or as a full endpoint URL — the https:// prefix and .documents.azure.com suffix
    will be added automatically if missing.
    """
    return list_databases(account)


@app.tool()
def cosmosdb_list_containers(account: str, database: str) -> str:
    """List all containers in a Cosmos DB database.

    Returns a sorted JSON array of container names.
    The account can be given as a short name or full endpoint URL.
    """
    return list_containers(account, database)


@app.tool()
def cosmosdb_get_container_info(account: str, database: str, container: str) -> str:
    """Get metadata for a Cosmos DB container.

    Returns partition key path, indexing policy, default TTL, unique key policy,
    and system properties (_self, _etag, _ts).
    The account can be given as a short name or full endpoint URL.
    """
    return get_container_info(account, database, container)


@app.tool()
def cosmosdb_query_items(
    account: str,
    database: str,
    container: str,
    query: str,
    max_items: int = 100,
) -> str:
    """Run a SQL query against a Cosmos DB container and return results.

    Uses Cosmos DB SQL API syntax, e.g.:
      SELECT * FROM c WHERE c.status = 'active'
      SELECT c.id, c.name FROM c ORDER BY c._ts DESC

    max_items is capped at 1000. Cross-partition queries are enabled automatically.
    Use cosmosdb_query_items_to_file instead if the result set may be large.
    """
    return query_items(account, database, container, query, max_items)


@app.tool()
def cosmosdb_query_items_to_file(
    account: str,
    database: str,
    container: str,
    query: str,
    output_file: str,
    max_items: int = 100,
) -> str:
    """Run a SQL query against a Cosmos DB container and save results to a file.

    Results are written to output_file as a JSON array.
    Only the item count is returned in context — use this variant when the result
    set may be large to avoid filling the context window.
    max_items is capped at 1000.
    """
    return query_items(account, database, container, query, max_items, save_to=output_file)


@app.tool()
def cosmosdb_count_items(
    account: str,
    database: str,
    container: str,
    where: str | None = None,
) -> str:
    """Count items in a Cosmos DB container, with an optional filter.

    where accepts a SQL WHERE clause body (without the WHERE keyword), e.g.:
      c.status = 'active'
      c.createdAt > '2025-01-01'

    If where is omitted, counts all items in the container.
    Returns a JSON object with a 'count' field.
    """
    return count_items(account, database, container, where)


@app.tool()
def cosmosdb_read_item(
    account: str,
    database: str,
    container: str,
    item_id: str,
    partition_key: str,
) -> str:
    """Read a single item from a Cosmos DB container by ID and partition key.

    Returns the full item document as JSON.
    Both item_id and partition_key are required — Cosmos DB requires the partition
    key for efficient point reads.
    """
    return read_item(account, database, container, item_id, partition_key)


@app.tool()
def cosmosdb_upsert_item(
    account: str,
    database: str,
    container: str,
    item: dict,
) -> str:
    """Insert or replace an item in a Cosmos DB container.

    The item must include an 'id' field. If an item with the same id and partition
    key already exists it will be replaced; otherwise a new item is created.
    Returns the stored item document (including system fields) as JSON.
    """
    return upsert_item(account, database, container, item)


@app.tool()
def cosmosdb_delete_item(
    account: str,
    database: str,
    container: str,
    item_id: str,
    partition_key: str,
) -> str:
    """Delete an item from a Cosmos DB container.

    THIS IS DESTRUCTIVE — the item cannot be recovered after deletion.
    Both item_id and partition_key are required.
    """
    return delete_item(account, database, container, item_id, partition_key)


# ── Service Bus ──────────────────────────────────────────────────────────────

@app.tool()
def servicebus_list_namespaces() -> str:
    """List all Azure Service Bus namespaces in the current subscription.

    The subscription is resolved automatically — first from the AZURE_SUBSCRIPTION_ID
    environment variable, then from the active 'az login' session. If neither is
    available, an error is returned with instructions.
    """
    return list_namespaces()


@app.tool()
def servicebus_list_queues(namespace: str) -> str:
    """List all queues in an Azure Service Bus namespace.

    Returns a sorted JSON array of queue names.
    The namespace can be given as a short name (e.g. shdapps-dev1-eus2-sbn)
    or as a fully qualified hostname — the .servicebus.windows.net suffix will
    be appended automatically if missing.
    """
    return list_queues(namespace)


@app.tool()
def servicebus_list_topics(namespace: str, include_subscriptions: bool = False) -> str:
    """List all topics in an Azure Service Bus namespace.

    Returns a sorted JSON array of topic names. If include_subscriptions is true,
    returns a JSON object mapping each topic name to a sorted array of its subscription names.
    The namespace can be given as a short name or fully qualified hostname.
    """
    return list_topics(namespace, include_subscriptions)


@app.tool()
def servicebus_send_message(
    namespace: str,
    queue: str,
    body: str,
    session_id: str | None = None,
    correlation_id: str | None = None,
    application_properties: dict[str, str] | None = None,
    scheduled_enqueue_time: str | None = None,
) -> str:
    """Send a single message to an Azure Service Bus queue or topic.

    The namespace can be given as a short name or fully qualified hostname.

    scheduled_enqueue_time accepts an ISO 8601 string (e.g. '2026-03-05T10:00:00Z').
    If provided, the message will be enqueued at that time rather than immediately.

    Auth uses DefaultAzureCredential. Ensure you have run 'az login' before use.
    """
    return send_message(namespace, queue, body, session_id, correlation_id, application_properties, scheduled_enqueue_time)


@app.tool()
def servicebus_send_batch(
    namespace: str,
    queue: str,
    messages: list[dict],
) -> str:
    """Send multiple messages to an Azure Service Bus queue or topic in a single batch.

    Each message in the 'messages' array should have:
      - body (string, required): the message content
      - session_id (string, optional)
      - correlation_id (string, optional)
      - application_properties (object, optional): key/value map of custom properties
      - scheduled_enqueue_time (string, optional): ISO 8601 time to enqueue the message

    The entire batch is delivered in a single send operation. Useful for seeding test data.
    """
    return send_batch(namespace, queue, messages)


@app.tool()
def servicebus_peek_messages(
    namespace: str,
    queue: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus queue.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies and metadata (sequence number, enqueue time, properties).
    max_count is capped at 100.
    For session-enabled queues, provide a session_id to peek a specific session.
    If session_id is omitted on a session-enabled queue, the next available session
    is accepted, peeked, and immediately released.
    Use servicebus_peek_messages_to_file instead if message bodies may be large.
    """
    return peek_messages(namespace, queue, max_count, session_id)


@app.tool()
def servicebus_peek_messages_to_file(
    namespace: str,
    queue: str,
    output_file: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus queue, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (sequence number, enqueue time, properties) is returned in context —
    use this variant when message bodies may be large to avoid filling the context window.
    """
    return peek_messages(namespace, queue, max_count, session_id, save_bodies_to=output_file)


@app.tool()
def servicebus_peek_dlq(
    namespace: str,
    queue: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for an Azure Service Bus queue.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies, dead letter reason, error description, and other metadata.
    max_count is capped at 100.
    Use servicebus_peek_dlq_to_file instead if message bodies may be large.
    """
    return peek_dlq(namespace, queue, max_count)


@app.tool()
def servicebus_peek_dlq_to_file(
    namespace: str,
    queue: str,
    output_file: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for an Azure Service Bus queue, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (dead letter reason, error description, sequence number, enqueue time) is returned in context.
    """
    return peek_dlq(namespace, queue, max_count, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_dlq(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from the dead letter queue for an Azure Service Bus queue.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_dlq(namespace, queue, max_messages)


@app.tool()
def servicebus_requeue_dlq(
    namespace: str,
    queue: str,
    max_messages: int = 100,
) -> str:
    """Move messages from a queue's dead letter queue back to the main queue.

    Each message is re-sent to the main queue preserving body, session_id, correlation_id,
    and application_properties, then completed (removed) from the dead letter queue.
    Stops if the running total would exceed max_messages.
    """
    return requeue_dlq(namespace, queue, max_messages)


@app.tool()
def servicebus_purge_queue(
    namespace: str,
    queue: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus queue.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_queue(namespace, queue, max_messages)


@app.tool()
def servicebus_peek_subscription_messages(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies and metadata (sequence number, enqueue time, properties).
    max_count is capped at 100.
    Use servicebus_peek_subscription_messages_to_file instead if message bodies may be large.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count, session_id)


@app.tool()
def servicebus_peek_subscription_messages_to_file(
    namespace: str,
    topic: str,
    subscription: str,
    output_file: str,
    max_count: int = 10,
    session_id: str | None = None,
) -> str:
    """Non-destructively peek at messages in an Azure Service Bus topic subscription, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (sequence number, enqueue time, properties) is returned in context.
    """
    return peek_subscription_messages(namespace, topic, subscription, max_count, session_id, save_bodies_to=output_file)


@app.tool()
def servicebus_peek_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for a topic subscription.

    Messages are not locked or consumed — this is a read-only operation.
    Returns message bodies, dead letter reason, error description, and other metadata.
    max_count is capped at 100.
    Use servicebus_peek_subscription_dlq_to_file instead if message bodies may be large.
    """
    return peek_subscription_dlq(namespace, topic, subscription, max_count)


@app.tool()
def servicebus_peek_subscription_dlq_to_file(
    namespace: str,
    topic: str,
    subscription: str,
    output_file: str,
    max_count: int = 10,
) -> str:
    """Non-destructively peek at messages in the dead letter queue for a topic subscription, saving bodies to a file.

    Message bodies are written to output_file as JSON (keyed by sequence number).
    Only metadata (dead letter reason, error description, sequence number, enqueue time) is returned in context.
    """
    return peek_subscription_dlq(namespace, topic, subscription, max_count, save_bodies_to=output_file)


@app.tool()
def servicebus_purge_subscription(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from an Azure Service Bus topic subscription.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_subscription(namespace, topic, subscription, max_messages)


@app.tool()
def servicebus_purge_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 1000,
) -> str:
    """Delete all messages from the dead letter queue for a topic subscription.

    THIS IS DESTRUCTIVE — messages cannot be recovered after purging.
    Stops and leaves remaining messages untouched if the running total exceeds max_messages.
    """
    return purge_subscription_dlq(namespace, topic, subscription, max_messages)


@app.tool()
def servicebus_requeue_subscription_dlq(
    namespace: str,
    topic: str,
    subscription: str,
    max_messages: int = 100,
) -> str:
    """Move messages from a topic subscription's dead letter queue back to the topic.

    Each message is re-sent to the topic preserving body, session_id, correlation_id,
    and application_properties, then completed (removed) from the dead letter queue.
    Stops if the running total would exceed max_messages.
    """
    return requeue_subscription_dlq(namespace, topic, subscription, max_messages)


# ── Authorization / PIM ──────────────────────────────────────────────────────

@app.tool()
def authorization_list_eligible_roles() -> str:
    """List all Azure PIM roles you are eligible to activate, across all accessible subscriptions.

    Returns role name, scope, eligibility status, and whether the eligibility is permanent or time-limited.
    Use this to discover what roles are available before calling authorization_activate_role.
    """
    return list_eligible_roles()


@app.tool()
def authorization_activate_role(
    role: str,
    scope: str,
    justification: str,
    duration: str | None = None,
) -> str:
    """Activate an eligible Azure PIM role assignment.

    role: the role name exactly as returned by authorization_list_eligible_roles (e.g. 'Contributor')
    scope: the scope to activate on, exactly as returned by authorization_list_eligible_roles
    justification: reason for activation (required by Azure PIM)
    duration: optional ISO 8601 duration string (e.g. 'PT4H', 'PT30M'). Defaults to the
              maximum duration allowed by the role's policy. Capped at the policy maximum if exceeded.

    Returns the activation status and request ID. Status 'Provisioned' means immediately active.
    Status 'PendingApproval' or 'PendingApprovalProvisioning' means an approver must act first.
    """
    return activate_role(role, scope, justification, duration)


def main():
    app.run()


if __name__ == "__main__":
    main()
