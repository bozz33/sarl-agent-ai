BEGIN;

ALTER TABLE project_memory_chunks
    ALTER COLUMN embedding TYPE vector(768)
    USING embedding::vector(768);

CREATE INDEX IF NOT EXISTS idx_project_memory_chunks_embedding_hnsw
    ON project_memory_chunks
    USING hnsw (embedding vector_cosine_ops);

COMMIT;
