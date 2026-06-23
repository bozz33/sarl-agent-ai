#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import statistics
import time

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


URL = "http://127.0.0.1:8000/mcp"


async def one_session() -> float:
    started = time.perf_counter()
    async with streamable_http_client(URL) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            if len(result.tools) < 7:
                raise RuntimeError(f"unexpected MCP tool count: {len(result.tools)}")
    return time.perf_counter() - started


async def run() -> None:
    durations: list[float] = []
    for _ in range(4):
        durations.extend(await asyncio.gather(*(one_session() for _ in range(25))))
    ordered = sorted(durations)
    p95 = ordered[max(0, int(len(ordered) * 0.95) - 1)]
    print(
        "MCP_SESSION_STRESS_OK "
        f"sessions={len(durations)} "
        f"mean_ms={statistics.mean(durations) * 1000:.1f} "
        f"p95_ms={p95 * 1000:.1f} "
        f"max_ms={max(durations) * 1000:.1f}"
    )


if __name__ == "__main__":
    asyncio.run(run())
