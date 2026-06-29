# NAUTILUS-MCP-INTEGRATION.md

How Hermes reaches the backtest engine — same pattern as project-memory-mcp.

## Shape
```
trading agent (Hermes)
  -> MCP tool (sarl_nautilus_runner)
  -> http://nautilus-runner-mcp:8200/mcp  (streamable-HTTP)
  -> services/nautilus-runner/app/mcp_server.py
  -> guards + BacktestEngine
  -> artifacts + journal
```

## Exposed MCP tools (allow-listed, backtest only)
- `nautilus_validate_environment` — guards + nautilus version + settings.
- `nautilus_run_backtest(strategy, dataset)` — runs the allow-listed backtest,
  returns the summary dict.
- `nautilus_generate_report(last)` — returns the latest summary.json.

No live tool is exposed. The server runs the same hard guards as the CLI.

## Wiring
- Compose service `nautilus-runner-mcp` (image `sarl/nautilus-runner:0.2.0`),
  on the `default` network, reachable by hermes-agent.
- `scripts/configure-active-profiles.py` attaches the `sarl_nautilus_runner`
  MCP **only to the trading agents** (`TRADING_AGENTS`).

## Deploy (human-gated)
Not auto-deployed. To activate on the live stack:
```
docker compose up -d nautilus-runner-mcp
python scripts/configure-active-profiles.py        # regenerate profile configs
# restart gateway so trading agents pick up the new MCP
```
Verify boot: container healthy, `GET /mcp` returns HTTP 406 (expected for a raw
GET without MCP headers), `nautilus_validate_environment` returns ok.

## Verified (2026-06-29)
Server boots (Uvicorn on 8200), `/mcp` reachable (406 on raw GET), MCP exposes
exactly the 3 allow-listed tools, 18 tests pass. Image `sarl/nautilus-runner:0.2.0`.
