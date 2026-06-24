#!/usr/bin/env bash
# Initialise (idempotent) les projets autorises dans la base MCP project-memory.
#
# Le service MCP lit la table `projects` mais ne cree jamais de projet: sans cette
# initialisation, project_context_get/write echouent ("active project not found")
# et la persistance inter-sessions est inactive.
#
# Cree une ligne `projects` (status=active) pour chaque id de
# SARL_MEMORY_ALLOWED_PROJECTS. A relancer apres un reset de la base.
#
# Usage: scripts/init-project-memory.sh   (le conteneur sarl-project-memory-mcp doit tourner)

set -euo pipefail

CONTAINER="${MCP_CONTAINER:-sarl-project-memory-mcp}"

docker exec -i "$CONTAINER" python - <<'PY'
import asyncio
from sarl_project_memory_mcp.config import Settings
from sarl_project_memory_mcp.db import ProjectMemoryDatabase


async def main() -> None:
    settings = Settings.from_env()
    db = ProjectMemoryDatabase(settings.database_url)
    await db.open()
    try:
        async with db._require_pool().connection() as conn:
            for pid in sorted(settings.allowed_projects):
                name = pid.replace("-", " ").title()
                await conn.execute(
                    "INSERT INTO projects (id, name, status) VALUES (%s, %s, 'active') "
                    "ON CONFLICT (id) DO UPDATE SET status='active'",
                    (pid, name),
                )
                print(f"projet initialise: {pid} (active)")
            cur = await conn.execute("SELECT id, name, status FROM projects")
            print("projects:", await cur.fetchall())
    finally:
        await db.close()


asyncio.run(main())
PY
