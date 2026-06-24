from __future__ import annotations

from decimal import Decimal
from typing import Any, Protocol

from .policy import validate_memory_write, validate_project
from .schemas import MEMORY_TYPES, TRUTH_STATUSES, MemoryWrite, MemoryValidationError


class MemoryRepository(Protocol):
    async def project_exists(self, project_id: str) -> bool: ...
    async def context_get(self, project_id: str) -> dict[str, Any] | None: ...
    async def write(self, memory: MemoryWrite) -> dict[str, Any]: ...
    async def write_chunk(
        self,
        memory_id: str,
        project_id: str,
        chunk_text: str,
        embedding: list[float],
    ) -> None: ...
    async def search(
        self,
        project_id: str,
        query: str,
        memory_type: str | None,
        truth_status: str | None,
        limit: int,
        query_embedding: list[float] | None,
    ) -> list[dict[str, Any]]: ...
    async def list_recent(self, project_id: str, limit: int) -> list[dict[str, Any]]: ...
    async def get(self, memory_id: str) -> dict[str, Any] | None: ...
    async def decision_log(self, project_id: str) -> list[dict[str, Any]]: ...
    async def summary(self, project_id: str) -> dict[str, Any]: ...
    async def supersede(
        self, old_memory_id: str, replacement: MemoryWrite
    ) -> dict[str, Any]: ...
    async def deprecate(self, memory_id: str) -> dict[str, Any] | None: ...
    async def healthcheck(self) -> dict[str, Any]: ...


class ProjectMemoryTools:
    def __init__(
        self,
        repository: MemoryRepository,
        allowed_projects: frozenset[str],
        max_search_results: int = 20,
        embeddings: Any | None = None,
    ) -> None:
        self.repository = repository
        self.allowed_projects = allowed_projects
        self.max_search_results = max_search_results
        self.embeddings = embeddings

    def _project(self, project_id: str) -> str:
        return validate_project(project_id, self.allowed_projects)

    async def _require_existing_project(self, project_id: str) -> str:
        project_id = self._project(project_id)
        if not await self.repository.project_exists(project_id):
            raise MemoryValidationError(f"active project not found: {project_id}")
        return project_id

    async def context_get(self, project_id: str) -> dict[str, Any]:
        project_id = await self._require_existing_project(project_id)
        result = await self.repository.context_get(project_id)
        if result is None:
            raise MemoryValidationError(f"project not found: {project_id}")
        return result

    async def memory_write(self, **kwargs: Any) -> dict[str, Any]:
        memory = validate_memory_write(
            allowed_projects=self.allowed_projects,
            **kwargs,
        )
        await self._require_existing_project(memory.project_id)
        result = await self.repository.write(memory)
        embedding_status = "disabled"
        if self.embeddings is not None and self.embeddings.enabled:
            try:
                embedding = await self.embeddings.embed_document(memory.content)
                if embedding is not None:
                    await self.repository.write_chunk(
                        str(result["id"]),
                        memory.project_id,
                        memory.content,
                        embedding,
                    )
                    embedding_status = "stored"
            except Exception:
                embedding_status = "unavailable"
        result["embedding_status"] = embedding_status
        return result

    async def memory_search(
        self,
        project_id: str,
        query: str,
        type: str | None = None,
        truth_status: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        project_id = await self._require_existing_project(project_id)
        query = query.strip()
        if not query:
            raise MemoryValidationError("query is required")
        if type is not None and type not in MEMORY_TYPES:
            raise MemoryValidationError(f"unsupported memory type: {type}")
        if truth_status is not None and truth_status not in TRUTH_STATUSES:
            raise MemoryValidationError(f"unsupported truth_status: {truth_status}")
        limit = max(1, min(limit, self.max_search_results))
        query_embedding = None
        if self.embeddings is not None and self.embeddings.enabled:
            try:
                query_embedding = await self.embeddings.embed_query(query)
            except Exception:
                query_embedding = None
        return await self.repository.search(
            project_id,
            query,
            type,
            truth_status,
            limit,
            query_embedding,
        )

    async def decision_log(self, project_id: str) -> list[dict[str, Any]]:
        project_id = await self._require_existing_project(project_id)
        return await self.repository.decision_log(project_id)

    async def summary(self, project_id: str) -> dict[str, Any]:
        project_id = await self._require_existing_project(project_id)
        return await self.repository.summary(project_id)

    async def list_recent(
        self, project_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        project_id = await self._require_existing_project(project_id)
        limit = max(1, min(limit, self.max_search_results))
        return await self.repository.list_recent(project_id, limit)

    async def memory_get(self, project_id: str, memory_id: str) -> dict[str, Any]:
        project_id = await self._require_existing_project(project_id)
        result = await self.repository.get(memory_id)
        if result is None or result.get("project_id") != project_id:
            raise MemoryValidationError("memory not found in project")
        return result

    async def memory_supersede(
        self,
        project_id: str,
        old_memory_id: str,
        new_content: str,
        created_by_profile: str | None = None,
        validated_by: str | None = None,
        confidence: float | str | Decimal = Decimal("0.70"),
    ) -> dict[str, Any]:
        project_id = await self._require_existing_project(project_id)
        old = await self.repository.get(old_memory_id)
        if old is None or old.get("project_id") != project_id:
            raise MemoryValidationError("memory not found in project")
        old_type = old["type"]
        new_truth = "decision" if old_type == "decision" else "confirmed"
        replacement = validate_memory_write(
            allowed_projects=self.allowed_projects,
            project_id=project_id,
            type=old_type,
            content=new_content,
            truth_status=new_truth,
            source_type="supersede",
            created_by_profile=created_by_profile,
            validated_by=validated_by,
            confidence=confidence,
            tags=old.get("tags") or (),
            metadata={"supersedes": old_memory_id},
            supersedes_id=old_memory_id,
        )
        result = await self.repository.supersede(old_memory_id, replacement)
        embedding_status = "disabled"
        if self.embeddings is not None and self.embeddings.enabled:
            try:
                embedding = await self.embeddings.embed_document(new_content)
                if embedding is not None:
                    new_memory = result["new_memory"]
                    await self.repository.write_chunk(
                        str(new_memory["id"]),
                        project_id,
                        new_content,
                        embedding,
                    )
                    embedding_status = "stored"
            except Exception:
                embedding_status = "unavailable"
        result["embedding_status"] = embedding_status
        return result

    async def memory_deprecate(
        self, project_id: str, memory_id: str
    ) -> dict[str, Any]:
        project_id = await self._require_existing_project(project_id)
        existing = await self.repository.get(memory_id)
        if existing is None or existing.get("project_id") != project_id:
            raise MemoryValidationError("memory not found in project")
        result = await self.repository.deprecate(memory_id)
        return {"deprecated": result is not None, "memory": result}

    async def healthcheck(self) -> dict[str, Any]:
        status = await self.repository.healthcheck()
        status["allowed_projects"] = sorted(self.allowed_projects)
        status["embeddings"] = (
            "enabled"
            if self.embeddings is not None
            and getattr(self.embeddings, "enabled", False)
            else "disabled"
        )
        return status
