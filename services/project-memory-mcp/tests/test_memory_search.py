from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sarl_project_memory_mcp.schemas import MemoryValidationError, MemoryWrite
from sarl_project_memory_mcp.tools import ProjectMemoryTools


class FakeRepository:
    def __init__(self) -> None:
        self.projects = {"sarl-agent-ai"}
        self.last_search: tuple[Any, ...] | None = None
        self.last_chunk: tuple[Any, ...] | None = None

    async def project_exists(self, project_id: str) -> bool:
        return project_id in self.projects

    async def search(self, *args: Any) -> list[dict[str, Any]]:
        self.last_search = args
        return [{"project_id": args[0], "content": "result"}]

    async def context_get(self, project_id: str) -> dict[str, Any]:
        return {"project": {"id": project_id}}

    async def write(self, memory: MemoryWrite) -> dict[str, Any]:
        return {
            "id": "00000000-0000-0000-0000-000000000001",
            "project_id": memory.project_id,
            "content": memory.content,
        }

    async def write_chunk(
        self,
        memory_id: str,
        project_id: str,
        chunk_text: str,
        embedding: list[float],
    ) -> None:
        self.last_chunk = (memory_id, project_id, chunk_text, embedding)

    async def list_recent(self, project_id: str, limit: int) -> list[dict[str, Any]]:
        return []

    async def get(self, memory_id: str) -> dict[str, Any] | None:
        return None

    async def decision_log(self, project_id: str) -> list[dict[str, Any]]:
        return []

    async def summary(self, project_id: str) -> dict[str, Any]:
        return {"project_id": project_id}

    async def supersede(
        self, old_memory_id: str, replacement: MemoryWrite
    ) -> dict[str, Any]:
        return {}


class MemorySearchTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.repository = FakeRepository()
        self.tools = ProjectMemoryTools(
            self.repository, frozenset({"sarl-agent-ai"}), max_search_results=20
        )

    async def test_search_is_scoped_to_project(self) -> None:
        result = await self.tools.memory_search(
            "sarl-agent-ai", "fallback", type="decision", limit=200
        )
        self.assertEqual(result[0]["project_id"], "sarl-agent-ai")
        self.assertEqual(
            self.repository.last_search,
            ("sarl-agent-ai", "fallback", "decision", None, 20, None),
        )

    async def test_search_rejects_other_project(self) -> None:
        with self.assertRaises(MemoryValidationError):
            await self.tools.memory_search("other-project", "query")

    async def test_search_rejects_empty_query(self) -> None:
        with self.assertRaises(MemoryValidationError):
            await self.tools.memory_search("sarl-agent-ai", " ")


class FakeEmbeddings:
    enabled = True

    async def embed_document(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    async def embed_query(self, text: str) -> list[float]:
        return [0.3, 0.2, 0.1]


class SemanticMemoryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.repository = FakeRepository()
        self.tools = ProjectMemoryTools(
            self.repository,
            frozenset({"sarl-agent-ai"}),
            embeddings=FakeEmbeddings(),
        )

    async def test_write_stores_embedding(self) -> None:
        result = await self.tools.memory_write(
            project_id="sarl-agent-ai",
            type="fact",
            content="Les traitements asynchrones utilisent une file de tâches.",
            truth_status="confirmed",
        )
        self.assertEqual(result["embedding_status"], "stored")
        self.assertEqual(
            self.repository.last_chunk,
            (
                "00000000-0000-0000-0000-000000000001",
                "sarl-agent-ai",
                "Les traitements asynchrones utilisent une file de tâches.",
                [0.1, 0.2, 0.3],
            ),
        )

    async def test_search_passes_query_embedding(self) -> None:
        await self.tools.memory_search("sarl-agent-ai", "travail en arrière-plan")
        self.assertEqual(
            self.repository.last_search,
            (
                "sarl-agent-ai",
                "travail en arrière-plan",
                None,
                None,
                10,
                [0.3, 0.2, 0.1],
            ),
        )

    async def test_embedding_failure_falls_back_to_lexical_search(self) -> None:
        class FailingEmbeddings(FakeEmbeddings):
            async def embed_query(self, text: str) -> list[float]:
                raise RuntimeError("provider unavailable")

        tools = ProjectMemoryTools(
            self.repository,
            frozenset({"sarl-agent-ai"}),
            embeddings=FailingEmbeddings(),
        )
        await tools.memory_search("sarl-agent-ai", "fallback")
        self.assertIsNone(self.repository.last_search[-1])


if __name__ == "__main__":
    unittest.main()
