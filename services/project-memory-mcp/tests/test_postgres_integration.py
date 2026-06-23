from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sarl_project_memory_mcp.db import ProjectMemoryDatabase
from sarl_project_memory_mcp.tools import ProjectMemoryTools


DATABASE_URL = os.environ.get("SARL_MEMORY_TEST_DATABASE_URL")


@unittest.skipUnless(DATABASE_URL, "SARL_MEMORY_TEST_DATABASE_URL not set")
class PostgresIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.database = ProjectMemoryDatabase(DATABASE_URL or "")
        await self.database.open()
        async with self.database._require_pool().connection() as conn:
            await conn.execute(
                """
                INSERT INTO projects (id, name)
                VALUES ('sarl-agent-ai', 'SARL-Agent-AI integration test')
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                """
            )
        self.tools = ProjectMemoryTools(
            self.database, frozenset({"sarl-agent-ai"}), max_search_results=20
        )

    async def asyncTearDown(self) -> None:
        async with self.database._require_pool().connection() as conn:
            await conn.execute(
                "DELETE FROM project_memory WHERE project_id = 'sarl-agent-ai'"
            )
            await conn.execute("DELETE FROM projects WHERE id = 'sarl-agent-ai'")
        await self.database.close()

    async def test_write_search_get_and_supersede(self) -> None:
        created = await self.tools.memory_write(
            project_id="sarl-agent-ai",
            type="decision",
            content="Le fallback technique gere les pannes et quotas.",
            truth_status="decision",
            created_by_profile="integration-test",
            confidence=0.9,
            tags=["routing", "fallback"],
        )
        memory_id = str(created["id"])

        found = await self.tools.memory_search(
            "sarl-agent-ai", "fallback technique", type="decision"
        )
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["project_id"], "sarl-agent-ai")

        fetched = await self.tools.memory_get("sarl-agent-ai", memory_id)
        self.assertEqual(str(fetched["id"]), memory_id)

        superseded = await self.tools.memory_supersede(
            "sarl-agent-ai",
            memory_id,
            "Le fallback technique gere uniquement pannes, quotas et indisponibilites.",
            created_by_profile="integration-test",
        )
        self.assertEqual(
            str(superseded["new_memory"]["supersedes_id"]), memory_id
        )

        old = await self.tools.memory_get("sarl-agent-ai", memory_id)
        self.assertEqual(old["truth_status"], "superseded")


if __name__ == "__main__":
    unittest.main()
