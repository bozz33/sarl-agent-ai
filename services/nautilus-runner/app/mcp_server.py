"""MCP server exposing nautilus-runner to Hermes.

Only allow-listed, backtest-only tools are exposed. Every tool runs the hard
guards (via app.runner / app.guards). No live tool exists here. Hermes reaches
this server over streamable-HTTP at /mcp, the same pattern as project-memory-mcp.
"""

from __future__ import annotations

import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from app import config, guards

mcp = FastMCP(
    "SARL Nautilus Runner",
    json_response=True,
    host=os.environ.get("NAUTILUS_MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("NAUTILUS_MCP_PORT", "8200")),
    streamable_http_path="/mcp",
)


@mcp.tool()
def nautilus_validate_environment() -> dict[str, Any]:
    """Check guards + NautilusTrader availability. Returns settings and scanned strategies."""
    guards.assert_paper_only()
    scanned = guards.scan_strategies_dir(config.STRATEGIES_DIR)
    import nautilus_trader

    return {
        "ok": True,
        "nautilus_version": nautilus_trader.__version__,
        "settings": config.RunnerSettings().as_dict(),
        "strategies_scanned": scanned,
    }


@mcp.tool()
def nautilus_run_backtest(strategy: str = "eurusd_ema_cross", dataset: str = "simulated_eurusd") -> dict[str, Any]:
    """Run an allow-listed backtest (simulation only). Returns the summary dict.

    Refuses any strategy outside the allow-list and any live keyword.
    """
    from app.runner import run_backtest

    return run_backtest(strategy=strategy, dataset=dataset)


@mcp.tool()
def nautilus_generate_report(last: bool = True) -> dict[str, Any]:
    """Return the latest backtest summary.json as a dict."""
    dirs = sorted(config.REPORTS_DIR.glob("BT-*"))
    if not dirs:
        return {"error": "no backtests found"}
    return json.loads((dirs[-1] / "summary.json").read_text(encoding="utf-8"))


def main() -> None:
    transport = os.environ.get("NAUTILUS_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise RuntimeError(f"unsupported MCP transport: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
