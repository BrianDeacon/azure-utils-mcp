# Azure Utils MCP Server

An MCP (Model Context Protocol) server for Azure development and operations. Compatible with any MCP client — Claude Code, Claude Desktop, Cursor, and others.

Covers three areas:

- **Cosmos DB** — list accounts, databases, and containers; run SQL queries; read, write, and delete documents
- **Service Bus** — list namespaces, queues, and topics; send messages; peek, purge, and requeue dead letter queues
- **Authorization / PIM** — list eligible roles and activate PIM role assignments

Authentication uses `DefaultAzureCredential`, which picks up an active `az login` session automatically. No secrets or connection strings are ever passed as tool arguments.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) with an active `az login` session

## Installation

### macOS

```bash
brew install uv azure-cli
```

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash   # Debian/Ubuntu
```

For other Linux distributions see the [Azure CLI install docs](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux).

### Windows

```powershell
winget install --id=astral-sh.uv
winget install --id=Microsoft.AzureCLI
```

## Configuration

**Claude Code** users:

```bash
claude mcp add --scope user azure-utils -- uvx azure-utils-mcp
```

For other MCP clients, add the following to your server configuration:

```json
{
  "mcpServers": {
    "azure-utils": {
      "command": "uvx",
      "args": ["azure-utils-mcp"]
    }
  }
}
```

Restart your MCP client after adding the server. Optional env vars:

- `AZURE_SUBSCRIPTION_ID` — used by list_accounts/list_namespaces if set; otherwise resolved from `az login`
- `AZURE_COSMOS_KEY` — key-based auth for Cosmos DB data plane operations
- `AZURE_SERVICEBUS_CONNECTION_STRING` — connection string auth for Service Bus operations

### Installing from source

```bash
git clone https://github.com/BrianDeacon/azure-utils-mcp
cd azure-utils-mcp
uv sync
az login
```

Then configure with the cloned path:

```json
{
  "mcpServers": {
    "azure-utils": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/azure-utils-mcp", "azure-utils-mcp"]
    }
  }
}
```

---

## Cosmos DB Tools

The `account` parameter accepts either a short account name (e.g. `my-cosmos-account`) or a full endpoint URL. The `https://` prefix and `.documents.azure.com` suffix are added automatically if missing.

### `cosmosdb_list_accounts`

List all Cosmos DB accounts in the current Azure subscription.

### `cosmosdb_list_databases`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |

### `cosmosdb_list_containers`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |

### `cosmosdb_get_container_info`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |

Returns partition key path, indexing policy, default TTL, unique key policy, and system properties.

### `cosmosdb_query_items`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `query` | string | yes | SQL query (e.g. `SELECT * FROM c WHERE c.status = 'active'`) |
| `max_items` | integer | no | Max items to return (default 100, cap 1000) |

### `cosmosdb_query_items_to_file`

Same as `cosmosdb_query_items` but writes results to a file. Use when result sets may be large.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `query` | string | yes | SQL query |
| `output_file` | string | yes | Path to write results as a JSON array |
| `max_items` | integer | no | Max items to return (default 100, cap 1000) |

### `cosmosdb_count_items`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `where` | string | no | SQL WHERE clause body (e.g. `c.status = 'active'`). If omitted, counts all items. |

### `cosmosdb_read_item`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `item_id` | string | yes | Item `id` field value |
| `partition_key` | string | yes | Partition key value |

### `cosmosdb_upsert_item`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `item` | object | yes | Full item document — must include an `id` field |

### `cosmosdb_delete_item`

**Destructive.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | yes | Cosmos DB account name or endpoint |
| `database` | string | yes | Database name |
| `container` | string | yes | Container name |
| `item_id` | string | yes | Item `id` field value |
| `partition_key` | string | yes | Partition key value |

---

## Service Bus Tools

The `namespace` parameter accepts either a short name (e.g. `my-namespace`) or a fully qualified hostname. The `.servicebus.windows.net` suffix is appended automatically if absent.

### `servicebus_list_namespaces`

List all Service Bus namespaces in the current Azure subscription.

### `servicebus_list_queues`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |

### `servicebus_list_topics`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `include_subscriptions` | boolean | no | If true, returns a map of topic → subscription names (default false) |

### `servicebus_send_message`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue or topic name |
| `body` | string | yes | Message body |
| `session_id` | string | no | Required for session-enabled queues |
| `correlation_id` | string | no | Correlation ID |
| `application_properties` | object | no | Key/value map of custom properties |
| `scheduled_enqueue_time` | string | no | ISO 8601 datetime to enqueue the message |

### `servicebus_send_batch`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue or topic name |
| `messages` | array | yes | Array of message objects, each with `body` (required), plus optional `session_id`, `correlation_id`, `application_properties`, `scheduled_enqueue_time` |

### `servicebus_peek_messages` / `servicebus_peek_messages_to_file`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_count` | integer | no | Max messages (default 10, cap 100) |
| `session_id` | string | no | Peek within a specific session |
| `output_file` | string | yes (to_file only) | Path to write message bodies |

### `servicebus_peek_dlq` / `servicebus_peek_dlq_to_file`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_count` | integer | no | Max messages (default 10, cap 100) |
| `output_file` | string | yes (to_file only) | Path to write message bodies |

### `servicebus_purge_queue` / `servicebus_purge_dlq`

**Destructive.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_messages` | integer | no | Safety cap (default 1000) |

### `servicebus_requeue_dlq`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `queue` | string | yes | Queue name |
| `max_messages` | integer | no | Safety cap (default 100) |

### `servicebus_peek_subscription_messages` / `servicebus_peek_subscription_messages_to_file`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_count` | integer | no | Max messages (default 10, cap 100) |
| `session_id` | string | no | Peek within a specific session |
| `output_file` | string | yes (to_file only) | Path to write message bodies |

### `servicebus_peek_subscription_dlq` / `servicebus_peek_subscription_dlq_to_file`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_count` | integer | no | Max messages (default 10, cap 100) |
| `output_file` | string | yes (to_file only) | Path to write message bodies |

### `servicebus_purge_subscription` / `servicebus_purge_subscription_dlq`

**Destructive.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_messages` | integer | no | Safety cap (default 1000) |

### `servicebus_requeue_subscription_dlq`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | yes | Service Bus namespace |
| `topic` | string | yes | Topic name |
| `subscription` | string | yes | Subscription name |
| `max_messages` | integer | no | Safety cap (default 100) |

---

## Authorization / PIM Tools

### `authorization_list_eligible_roles`

List all Azure PIM roles you are eligible to activate, across all accessible subscriptions. Returns role name, scope, and whether the eligibility is permanent or time-limited.

### `authorization_activate_role`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `role` | string | yes | Role name as returned by `authorization_list_eligible_roles` |
| `scope` | string | yes | Scope as returned by `authorization_list_eligible_roles` |
| `justification` | string | yes | Reason for activation |
| `duration` | string | no | ISO 8601 duration (e.g. `PT4H`). Defaults to the policy maximum. |

Returns activation status and request ID. `Provisioned` means immediately active; `PendingApproval` means an approver must act first.

---

## Security

- Authentication relies on `DefaultAzureCredential` — secrets and connection strings are never passed as tool arguments and will not appear in conversation history.
- `purge_*` and `requeue_*` tools enforce a `max_messages` safety cap to prevent accidental bulk operations.
- `cosmosdb_delete_item` is a hard point-delete requiring both item ID and partition key.
