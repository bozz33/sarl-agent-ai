BEGIN;

DROP INDEX IF EXISTS idx_project_memory_chunks_embedding_hnsw;

ALTER TABLE project_memory_chunks
    ALTER COLUMN embedding TYPE vector
    USING embedding::vector;

COMMIT;
