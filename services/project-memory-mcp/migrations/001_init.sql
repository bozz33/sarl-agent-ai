BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'disabled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL REFERENCES projects(id),
    type TEXT NOT NULL CHECK (
        type IN (
            'fact', 'hypothesis', 'decision', 'constraint', 'preference',
            'technical_note', 'incident', 'solution', 'risk',
            'meeting_summary', 'task_summary', 'handoff', 'report',
            'deprecated', 'superseded'
        )
    ),
    truth_status TEXT NOT NULL CHECK (
        truth_status IN (
            'hypothesis', 'confirmed', 'decision', 'deprecated', 'superseded'
        )
    ),
    content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 100000),
    source_type TEXT,
    source_path TEXT,
    source_url TEXT,
    created_by_profile TEXT,
    validated_by TEXT,
    confidence NUMERIC(3,2) NOT NULL DEFAULT 0.70
        CHECK (confidence BETWEEN 0 AND 1),
    supersedes_id UUID NULL REFERENCES project_memory(id),
    tags TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    search_document TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('simple'::regconfig, coalesce(content, ''))
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (type <> 'decision' OR truth_status = 'decision'),
    CHECK (type <> 'hypothesis' OR truth_status = 'hypothesis')
);

CREATE TABLE IF NOT EXISTS project_memory_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES project_memory(id) ON DELETE CASCADE,
    project_id TEXT NOT NULL REFERENCES projects(id),
    chunk_text TEXT NOT NULL,
    embedding vector,
    token_count INTEGER CHECK (token_count IS NULL OR token_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_project_memory_project
    ON project_memory(project_id);
CREATE INDEX IF NOT EXISTS idx_project_memory_type
    ON project_memory(project_id, type);
CREATE INDEX IF NOT EXISTS idx_project_memory_truth
    ON project_memory(project_id, truth_status);
CREATE INDEX IF NOT EXISTS idx_project_memory_created
    ON project_memory(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_memory_search
    ON project_memory USING GIN(search_document);
CREATE INDEX IF NOT EXISTS idx_project_memory_chunks_project
    ON project_memory_chunks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_memory_chunks_memory
    ON project_memory_chunks(memory_id);

COMMIT;
