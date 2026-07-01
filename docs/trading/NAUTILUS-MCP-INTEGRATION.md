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
- `nautilus_walk_forward` — bounded robustness pass.
- `nautilus_validate_ibkr` — read-only IBKR Paper validation.
- `nautilus_fetch_ibkr_data` — read-only historical data fetch from IBKR Paper.
- `nautilus_run_sweep` — bounded strategy/market sweep.
- `nautilus_research_iteration` — bounded research loop.
- `nautilus_proven_candidates` — journal query for robust candidates.
- `nautilus_robustness_ladder` — staged robustness validation.
- `nautilus_generate_report(last)` — returns the latest summary.json.
- `nautilus_daily_report` — daily digest.
- `nautilus_run_mission` — bounded mission runner.

No live tool is exposed. IBKR tools are paper/read-only. The server runs the
same hard guards as the CLI.

## Wiring
- Compose service `nautilus-runner-mcp` (image `sarl/nautilus-runner:0.12.1`),
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

## Verified (2026-07-01)
Server boots (Uvicorn on 8200), `/mcp` reachable (406 on raw GET), MCP exposes
12 allow-listed tools, 35 tests pass. Image `sarl/nautilus-runner:0.12.1`.
