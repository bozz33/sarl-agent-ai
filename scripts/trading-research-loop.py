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

    ladder = out.get("ladder_top", [])
    lines = ["🔬 TRADING RESEARCH LOOP (backtest only, no order)"]
    lines.append(f"iteration {out.get('iteration')} | window {out.get('window')} | "
                 f"{out.get('sweep_valid', '?')} valid configs")
    lines.append(f"ROBUSTNESS CEILING reached: level {out.get('ceiling_level', 0)} "
                 f"(distinct windows survived). proven: {out.get('proven_count', 0)}")
    if ladder:
        lines.append("Top of the ladder (level = windows survived / tested):")
        for c in ladder[:6]:
            lines.append(f"  L{c['times_robust']}/{c['times_tested']}  {c['strategy']} "
                         f"{c['market']} {c['timeframe']}  score={round(c.get('best_robust_score', 0), 2)}")
    refresh = out.get("refresh", {})
    if refresh.get("ok"):
        lines.append(f"history refreshed: {refresh.get('market')} ({refresh.get('bars')} bars)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
