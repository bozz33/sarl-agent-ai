"""The MCP server must expose only the allow-listed backtest tools."""

import asyncio


def test_only_allow_listed_tools_registered():
    from app import mcp_server

    tools = asyncio.run(mcp_server.mcp.list_tools())
    names = {t.name for t in tools}
    assert names == {
        "nautilus_validate_environment",
        "nautilus_run_backtest",
        "nautilus_walk_forward",
        "nautilus_validate_ibkr",
        "nautilus_fetch_ibkr_data",
        "nautilus_run_sweep",
        "nautilus_research_iteration",
        "nautilus_proven_candidates",
        "nautilus_robustness_ladder",
        "nautilus_generate_report",
        "nautilus_daily_report",
        "nautilus_run_mission",
    }
    # No live tool may ever appear here.
    for n in names:
        assert "live" not in n
        assert "real_money" not in n


def test_validate_environment_tool_runs():
    from app import mcp_server

    out = mcp_server.nautilus_validate_environment()
    assert out["ok"] is True
    assert out["settings"]["paper_only"] is True
