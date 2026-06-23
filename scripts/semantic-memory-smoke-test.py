#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
import uuid

import psycopg
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


PROJECT_ID = "sarl-agent-ai"
MARKER = f"semantic-smoke-{uuid.uuid4()}"
CONTENT = (
    "Le mécanisme de régulation réduit automatiquement la cadence des tâches "
    "asynchrones lorsque les ressources disponibles deviennent insuffisantes. "
    f"Marqueur de test: {MARKER}."
)


def payload(result: object) -> object:
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured.get("result", structured)
    content = getattr(result, "content", [])
    if content and hasattr(content[0], "text"):
        return json.loads(content[0].text)
    raise RuntimeError("MCP response does not contain a JSON payload")


async def run() -> None:
    database_url = os.environ["SARL_MEMORY_DATABASE_URL"]
    with psycopg.connect(database_url) as conn:
        conn.execute(
            """
            INSERT INTO projects (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, status = 'active'
            """,
            (PROJECT_ID, "Semantic smoke test"),
        )

    try:
        async with streamable_http_client("http://127.0.0.1:8000/mcp") as streams:
            read_stream, write_stream, _ = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                write_result = payload(
                    await session.call_tool(
                        "project_memory_write",
                        {
                            "project_id": PROJECT_ID,
                            "type": "fact",
                            "content": CONTENT,
                            "truth_status": "confirmed",
                            "source_type": "semantic-smoke-test",
                            "created_by_profile": "qa-agent",
                            "confidence": 0.99,
                            "tags": ["temporary", "semantic-smoke"],
                        },
                    )
                )
                if write_result["embedding_status"] != "stored":
                    raise RuntimeError(
                        f"embedding was not stored: {write_result!r}"
                    )
                memory_id = str(write_result["id"])

                search_result = payload(
                    await session.call_tool(
                        "project_memory_search",
                        {
                            "project_id": PROJECT_ID,
                            "query": (
                                "Comment ralentir le travail en arrière-plan "
                                "quand la machine manque de capacité ?"
                            ),
                            "limit": 5,
                        },
                    )
                )
                if not any(str(row["id"]) == memory_id for row in search_result):
                    raise RuntimeError(
                        f"semantic search did not retrieve fixture: {search_result!r}"
                    )
                print(
                    "SEMANTIC_MEMORY_SMOKE_OK "
                    f"id={memory_id} results={len(search_result)}"
                )
    finally:
        with psycopg.connect(database_url) as conn:
            conn.execute(
                "DELETE FROM project_memory WHERE project_id = %s",
                (PROJECT_ID,),
            )
            conn.execute("DELETE FROM projects WHERE id = %s", (PROJECT_ID,))


if __name__ == "__main__":
    asyncio.run(run())
