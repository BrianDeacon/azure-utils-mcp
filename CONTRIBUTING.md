# Contributing

Contributions are welcome. Here's how to get started.

## Setup

```bash
git clone https://github.com/BrianDeacon/azure-utils-mcp
cd azure-utils-mcp
uv sync
az login
```

Register the local version with your MCP client:

```bash
claude mcp add --scope user azure-utils -- uv run --directory /path/to/azure-utils-mcp azure-utils-mcp
```

## Project structure

Tools are organized into three subpackages:

- `src/azure_utils_mcp/tools/cosmosdb/` — Cosmos DB data plane tools
- `src/azure_utils_mcp/tools/servicebus/` — Service Bus send/peek/purge/requeue tools
- `src/azure_utils_mcp/tools/authorization/` — PIM role listing and activation

Each tool is a single `.py` file with a single handler function. `server.py` imports them all and exposes them via `@app.tool()` decorators. The shared `client.py` manages credential and client instances.

## Making changes

- Add new tools as a new file in the relevant subpackage
- Register new tools in `src/azure_utils_mcp/server.py` with an `@app.tool()` decorator
- The tool's docstring is what the AI reads — make it clear and accurate
- Test manually against real Azure resources before submitting

## Submitting a PR

- Open an issue first for anything non-trivial so we can align before you build it
- Keep PRs focused — one feature or fix per PR
- Update the README if you're adding or changing a tool

## Reporting bugs

Open an issue at https://github.com/BrianDeacon/azure-utils-mcp/issues with enough detail to reproduce it — which tool, what resource (redacted if needed), and what you expected vs. what happened.
