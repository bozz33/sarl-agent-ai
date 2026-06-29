#!/usr/bin/env python3
"""Trading daily digest — runs as a --no-agent cron on the default profile.

Calls the secured nautilus-runner MCP (backtest only) to generate the daily
report, prints it to stdout. The cron delivers stdout to Telegram. No LLM, no
live path. Mounted read-only into hermes-agent.
"""

from __future__ import annotations

import asyncio
import os

URL = os.environ.get("NAUTILUS_MCP_URL", "http://nautilus-runner-mcp:8200/mcp")


async def _digest() -> str:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("nautilus_daily_report", {})
            for block in result.content:
                text = getattr(block, "text", None)
                if text:
                    return text
    return ""


def main() -> int:
    try:
        out = asyncio.run(_digest())
    except Exception as exc:  # cron --no-agent: empty stdout = silent
        print(f"[trading-daily-digest] MCP error: {exc}")
        return 1
    if not out:
        return 0
    import json

    try:
        data = json.loads(out)
        body = data.get("report_md", out)
    except Exception:
        body = out
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
