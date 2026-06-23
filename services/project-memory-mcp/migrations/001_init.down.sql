BEGIN;

DROP TABLE IF EXISTS project_memory_chunks;
DROP TABLE IF EXISTS project_memory;
DROP TABLE IF EXISTS projects;

-- L'extension vector est partageable avec d'autres bases/usages.
-- Ne pas la supprimer automatiquement.

COMMIT;
