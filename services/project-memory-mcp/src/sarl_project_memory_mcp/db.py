from __future__ import annotations

from typing import Any

from .schemas import MemoryWrite


class ProjectMemoryDatabase:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.pool = None

    async def open(self) -> None:
        from psycopg.rows import dict_row
        from psycopg_pool import AsyncConnectionPool

        self.pool = AsyncConnectionPool(
            conninfo=self.database_url,
            min_size=1,
            max_size=3,
            num_workers=1,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        await self.pool.open()
        await self.pool.wait()

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()

    def _require_pool(self):
        if self.pool is None:
            raise RuntimeError("database pool is not open")
        return self.pool

    async def project_exists(self, project_id: str) -> bool:
        async with self._require_pool().connection() as conn:
            row = await conn.execute(
                "SELECT 1 FROM projects WHERE id = %s AND status = 'active'",
                (project_id,),
            )
            return await row.fetchone() is not None

    async def context_get(self, project_id: str) -> dict[str, Any] | None:
        async with self._require_pool().connection() as conn:
            project_cur = await conn.execute(
                "SELECT id, name, status, created_at, updated_at FROM projects WHERE id = %s",
                (project_id,),
            )
            project = await project_cur.fetchone()
            if project is None:
                return None
            counts_cur = await conn.execute(
                """
                SELECT type, truth_status, count(*) AS count
                FROM project_memory
                WHERE project_id = %s
                GROUP BY type, truth_status
                ORDER BY type, truth_status
                """,
                (project_id,),
            )
            recent_cur = await conn.execute(
                """
                SELECT id, type, truth_status, content, confidence, created_at
                FROM project_memory
                WHERE project_id = %s
                ORDER BY created_at DESC
                LIMIT 10
                """,
                (project_id,),
            )
            return {
                "project": project,
                "counts": await counts_cur.fetchall(),
                "recent": await recent_cur.fetchall(),
            }

    async def write(self, memory: MemoryWrite) -> dict[str, Any]:
        from psycopg.types.json import Jsonb

        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                """
                INSERT INTO project_memory (
                    project_id, type, truth_status, content, source_type,
                    source_path, source_url, created_by_profile, validated_by,
                    confidence, supersedes_id, tags, metadata
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING *
                """,
                (
                    memory.project_id,
                    memory.type,
                    memory.truth_status,
                    memory.content,
                    memory.source_type,
                    memory.source_path,
                    memory.source_url,
                    memory.created_by_profile,
                    memory.validated_by,
                    memory.confidence,
                    memory.supersedes_id,
                    list(memory.tags),
                    Jsonb(memory.metadata),
                ),
            )
            return await cur.fetchone()

    async def write_chunk(
        self,
        memory_id: str,
        project_id: str,
        chunk_text: str,
        embedding: list[float],
    ) -> None:
        vector = "[" + ",".join(f"{value:.9g}" for value in embedding) + "]"
        async with self._require_pool().connection() as conn:
            await conn.execute(
                """
                INSERT INTO project_memory_chunks (
                    memory_id, project_id, chunk_text, embedding
                )
                VALUES (%s, %s, %s, %s::vector)
                """,
                (memory_id, project_id, chunk_text, vector),
            )

    async def search(
        self,
        project_id: str,
        query: str,
        memory_type: str | None,
        truth_status: str | None,
        limit: int,
        query_embedding: list[float] | None,
    ) -> list[dict[str, Any]]:
        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                """
                SELECT id, project_id, type, truth_status, content, source_type,
                       source_path, source_url, created_by_profile, validated_by,
                       confidence, supersedes_id, tags, metadata, created_at,
                       updated_at,
                       ts_rank_cd(search_document, plainto_tsquery('simple', %s)) AS rank
                FROM project_memory
                WHERE project_id = %s
                  AND (%s::text IS NULL OR type = %s::text)
                  AND (%s::text IS NULL OR truth_status = %s::text)
                  AND (
                    search_document @@ plainto_tsquery('simple', %s)
                    OR content ILIKE '%%' || %s || '%%'
                  )
                ORDER BY rank DESC, created_at DESC
                LIMIT %s
                """,
                (
                    query,
                    project_id,
                    memory_type,
                    memory_type,
                    truth_status,
                    truth_status,
                    query,
                    query,
                    limit,
                ),
            )
            lexical = await cur.fetchall()
            if query_embedding is None:
                return lexical

            vector = (
                "["
                + ",".join(f"{value:.9g}" for value in query_embedding)
                + "]"
            )
            semantic_cur = await conn.execute(
                """
                SELECT pm.id, pm.project_id, pm.type, pm.truth_status,
                       pm.content, pm.source_type, pm.source_path,
                       pm.source_url, pm.created_by_profile, pm.validated_by,
                       pm.confidence, pm.supersedes_id, pm.tags, pm.metadata,
                       pm.created_at, pm.updated_at,
                       0::real AS rank,
                       1 - (pmc.embedding <=> %s::vector) AS semantic_score
                FROM project_memory_chunks pmc
                JOIN project_memory pm ON pm.id = pmc.memory_id
                WHERE pm.project_id = %s
                  AND (%s::text IS NULL OR pm.type = %s::text)
                  AND (%s::text IS NULL OR pm.truth_status = %s::text)
                  AND pmc.embedding IS NOT NULL
                ORDER BY pmc.embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    vector,
                    project_id,
                    memory_type,
                    memory_type,
                    truth_status,
                    truth_status,
                    vector,
                    limit,
                ),
            )
            semantic = await semantic_cur.fetchall()
            merged: dict[str, dict[str, Any]] = {}
            for row in lexical:
                row = dict(row)
                row["semantic_score"] = None
                merged[str(row["id"])] = row
            for row in semantic:
                row = dict(row)
                key = str(row["id"])
                if key in merged:
                    merged[key]["semantic_score"] = row["semantic_score"]
                else:
                    merged[key] = row
            return sorted(
                merged.values(),
                key=lambda row: (
                    float(row.get("rank") or 0)
                    + float(row.get("semantic_score") or 0)
                ),
                reverse=True,
            )[:limit]

    async def list_recent(self, project_id: str, limit: int) -> list[dict[str, Any]]:
        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                """
                SELECT *
                FROM project_memory
                WHERE project_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (project_id, limit),
            )
            return await cur.fetchall()

    async def get(self, memory_id: str) -> dict[str, Any] | None:
        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                "SELECT * FROM project_memory WHERE id = %s",
                (memory_id,),
            )
            return await cur.fetchone()

    async def decision_log(self, project_id: str) -> list[dict[str, Any]]:
        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                """
                SELECT *
                FROM project_memory
                WHERE project_id = %s
                  AND (type = 'decision' OR truth_status = 'decision')
                ORDER BY created_at DESC
                """,
                (project_id,),
            )
            return await cur.fetchall()

    async def summary(self, project_id: str) -> dict[str, Any]:
        async with self._require_pool().connection() as conn:
            counts = await conn.execute(
                """
                SELECT type, truth_status, count(*) AS count
                FROM project_memory
                WHERE project_id = %s
                GROUP BY type, truth_status
                ORDER BY count DESC, type, truth_status
                """,
                (project_id,),
            )
            latest = await conn.execute(
                """
                SELECT id, type, truth_status, content, created_at
                FROM project_memory
                WHERE project_id = %s
                  AND truth_status NOT IN ('deprecated', 'superseded')
                ORDER BY created_at DESC
                LIMIT 20
                """,
                (project_id,),
            )
            return {
                "project_id": project_id,
                "counts": await counts.fetchall(),
                "latest_active": await latest.fetchall(),
            }

    async def supersede(
        self, old_memory_id: str, replacement: MemoryWrite
    ) -> dict[str, Any]:
        from psycopg.types.json import Jsonb

        async with self._require_pool().connection() as conn:
            async with conn.transaction():
                old_cur = await conn.execute(
                    """
                    SELECT *
                    FROM project_memory
                    WHERE id = %s AND project_id = %s
                    FOR UPDATE
                    """,
                    (old_memory_id, replacement.project_id),
                )
                old = await old_cur.fetchone()
                if old is None:
                    raise LookupError("memory not found in project")
                new_cur = await conn.execute(
                    """
                    INSERT INTO project_memory (
                        project_id, type, truth_status, content, source_type,
                        source_path, source_url, created_by_profile, validated_by,
                        confidence, supersedes_id, tags, metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        replacement.project_id,
                        replacement.type,
                        replacement.truth_status,
                        replacement.content,
                        replacement.source_type,
                        replacement.source_path,
                        replacement.source_url,
                        replacement.created_by_profile,
                        replacement.validated_by,
                        replacement.confidence,
                        old_memory_id,
                        list(replacement.tags),
                        Jsonb(replacement.metadata),
                    ),
                )
                new = await new_cur.fetchone()
                await conn.execute(
                    """
                    UPDATE project_memory
                    SET truth_status = 'superseded',
                        type = CASE WHEN type = 'deprecated' THEN type ELSE 'superseded' END,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (old_memory_id,),
                )
                return {"old_memory_id": old_memory_id, "new_memory": new}

    async def deprecate(self, memory_id: str) -> dict[str, Any] | None:
        async with self._require_pool().connection() as conn:
            cur = await conn.execute(
                """
                UPDATE project_memory
                SET truth_status = 'deprecated',
                    updated_at = now()
                WHERE id = %s
                RETURNING *
                """,
                (memory_id,),
            )
            return await cur.fetchone()

    async def healthcheck(self) -> dict[str, Any]:
        async with self._require_pool().connection() as conn:
            ping = await conn.execute("SELECT 1 AS ok")
            ok = await ping.fetchone()
            counts = await conn.execute(
                "SELECT count(*) AS total FROM project_memory"
            )
            total = await counts.fetchone()
        return {
            "database": "ok" if ok else "error",
            "memory_rows": (total or {}).get("total"),
        }
