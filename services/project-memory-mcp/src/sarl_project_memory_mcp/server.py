from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
import asyncio
import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from .config import Settings
from .db import ProjectMemoryDatabase
from .embeddings import EmbeddingsDisabled, GeminiEmbeddings
from .tools import ProjectMemoryTools


@dataclass
class AppContext:
    tools: ProjectMemoryTools


_app_context: AppContext | None = None
_init_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    """Share one database pool across every streamable-HTTP MCP session.

    FastMCP may invoke this lifespan for each transport session. Creating a
    pool here unconditionally leaked several idle PostgreSQL connections per
    profile test/browser reconnect until max_connections was exhausted.
    """
    global _app_context
    if _app_context is None:
        async with _init_lock:
            if _app_context is None:
                settings = Settings.from_env()
                database = ProjectMemoryDatabase(settings.database_url)
                await database.open()
                if settings.embedding_provider == "gemini":
                    embeddings = GeminiEmbeddings(
                        api_key=settings.embedding_api_key,
                        model=settings.embedding_model
                        or "gemini-embedding-001",
                        dimension=settings.embedding_dimension,
                        timeout=settings.embedding_timeout,
                    )
                else:
                    embeddings = EmbeddingsDisabled()
                _app_context = AppContext(
                    tools=ProjectMemoryTools(
                        database,
                        settings.allowed_projects,
                        settings.max_search_results,
                        embeddings=embeddings,
                    )
                )
    if _app_context is None:
        raise RuntimeError("project memory context initialization failed")
    yield _app_context


mcp = FastMCP(
    "SARL Project Memory",
    lifespan=lifespan,
    json_response=True,
    host=os.environ.get("SARL_MEMORY_MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("SARL_MEMORY_MCP_PORT", "8000")),
    streamable_http_path="/mcp",
)


def _tools(ctx: Context[ServerSession, AppContext]) -> ProjectMemoryTools:
    return ctx.request_context.lifespan_context.tools


@mcp.tool()
async def project_context_get(
    project_id: str, ctx: Context[ServerSession, AppContext]
) -> dict[str, Any]:
    """Return project metadata, memory counts and recent entries."""
    return await _tools(ctx).context_get(project_id)


@mcp.tool()
async def project_memory_search(
    project_id: str,
    query: str,
    ctx: Context[ServerSession, AppContext],
    type: str | None = None,
    truth_status: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search memory inside one allowed project only."""
    return await _tools(ctx).memory_search(
        project_id, query, type, truth_status, limit
    )


@mcp.tool()
async def project_memory_write(
    project_id: str,
    type: str,
    content: str,
    truth_status: str,
    ctx: Context[ServerSession, AppContext],
    source_type: str | None = None,
    source_path: str | None = None,
    source_url: str | None = None,
    created_by_profile: str | None = None,
    validated_by: str | None = None,
    confidence: float = 0.70,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write policy-validated memory to one project."""
    return await _tools(ctx).memory_write(
        project_id=project_id,
        type=type,
        content=content,
        truth_status=truth_status,
        source_type=source_type,
        source_path=source_path,
        source_url=source_url,
        created_by_profile=created_by_profile,
        validated_by=validated_by,
        confidence=confidence,
        tags=tags,
        metadata=metadata,
    )


@mcp.tool()
async def project_memory_decision_log(
    project_id: str, ctx: Context[ServerSession, AppContext]
) -> list[dict[str, Any]]:
    """List project decisions newest first."""
    return await _tools(ctx).decision_log(project_id)


@mcp.tool()
async def project_memory_summary(
    project_id: str, ctx: Context[ServerSession, AppContext]
) -> dict[str, Any]:
    """Return memory counts and latest active entries for one project."""
    return await _tools(ctx).summary(project_id)


@mcp.tool()
async def project_memory_supersede(
    project_id: str,
    old_memory_id: str,
    new_content: str,
    ctx: Context[ServerSession, AppContext],
    created_by_profile: str | None = None,
    validated_by: str | None = None,
    confidence: float = 0.70,
) -> dict[str, Any]:
    """Create replacement memory and mark previous memory superseded."""
    return await _tools(ctx).memory_supersede(
        project_id,
        old_memory_id,
        new_content,
        created_by_profile,
        validated_by,
        confidence,
    )


@mcp.tool()
async def project_memory_list_recent(
    project_id: str,
    ctx: Context[ServerSession, AppContext],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List recent memories for one project."""
    return await _tools(ctx).list_recent(project_id, limit)


@mcp.tool()
async def project_memory_get(
    project_id: str,
    memory_id: str,
    ctx: Context[ServerSession, AppContext],
) -> dict[str, Any]:
    """Get one memory only when it belongs to the requested project."""
    return await _tools(ctx).memory_get(project_id, memory_id)


@mcp.tool()
async def project_memory_deprecate(
    project_id: str,
    memory_id: str,
    ctx: Context[ServerSession, AppContext],
) -> dict[str, Any]:
    """Mark one memory deprecated (no replacement) inside its project."""
    return await _tools(ctx).memory_deprecate(project_id, memory_id)


@mcp.tool()
async def project_memory_healthcheck(
    ctx: Context[ServerSession, AppContext],
) -> dict[str, Any]:
    """Return memory service health: database, row count, embeddings status."""
    return await _tools(ctx).healthcheck()


def main() -> None:
    transport = os.environ.get("SARL_MEMORY_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise RuntimeError(f"unsupported MCP transport: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
