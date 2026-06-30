#!/usr/bin/env python3
"""Autonomous research loop — runs as a --no-agent cron on the default profile.

Each firing: call the nautilus-runner MCP to run one research iteration
(refresh one market's long history when possible, sweep all families/timeframes,
accumulate candidate robustness), then report any PROVEN candidates (those that
survived walk-forward repeatedly). Stdout is delivered to Telegram. No LLM, no
order, backtest/simulation only.
"""

from __future__ import annotations

import asyncio
import json
import os

URL = os.environ.get("NAUTILUS_MCP_URL", "http://nautilus-runner-mcp:8200/mcp")


async def _call(tool: str, args: dict) -> dict:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            for block in result.content:
                text = getattr(block, "text", None)
                if text:
                    try:
                        return json.loads(text)
                    except Exception:
                        return {"raw": text}
    return {}


def main() -> int:
    try:
        out = asyncio.run(_call("nautilus_research_iteration", {}))
    except Exception as exc:
        print(f"[trading-research-loop] MCP error: {exc}")
        return 1

    proven = out.get("proven", [])
    by_tf = out.get("by_timeframe", {})
    lines = ["🔬 TRADING RESEARCH LOOP (backtest only, no order)"]
    lines.append(f"sweep: {out.get('sweep_valid', '?')} valid configs | proven candidates: {out.get('proven_count', 0)}")
    for tf, a in sorted(by_tf.items()):
        lines.append(f"  {tf}: {a.get('profitable')}/{a.get('configs')} profitable, mean PnL {a.get('mean_pnl')}")
    if proven:
        lines.append("PROVEN (survived walk-forward repeatedly):")
        for p in proven[:5]:
            lines.append(f"  - {p['strategy']} {p['market']} {p['timeframe']} | robust x{p['times_robust']}/{p['times_tested']} score={round(p.get('best_robust_score', 0), 2)}")
    else:
        lines.append("No proven candidate yet — keep accumulating (good: no overfit shortcut).")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
