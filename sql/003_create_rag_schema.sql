-- POLLY RAG Schema — Document embeddings for retrieval-augmented generation
-- Run: PGPASSWORD=mlfpass2026 psql -h 72.62.114.124 -U finespresso -d finespresso_db -f sql/003_create_rag_schema.sql

CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS polly_rag;

-- Source documents
CREATE TABLE IF NOT EXISTS polly_rag.documents (
    id              SERIAL PRIMARY KEY,
    filename        VARCHAR(500) NOT NULL UNIQUE,
    file_type       VARCHAR(20) NOT NULL,
    title           VARCHAR(500),
    file_size_bytes INTEGER,
    markdown_text   TEXT,
    chunk_count     INTEGER DEFAULT 0,
    processed_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly_rag.documents IS 'Source financial product documents processed for RAG retrieval.';

-- Document chunks with vector embeddings
CREATE TABLE IF NOT EXISTS polly_rag.chunks (
    id              SERIAL PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES polly_rag.documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    token_count     INTEGER,
    metadata        JSONB DEFAULT '{}',
    embedding       vector(384),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

COMMENT ON TABLE polly_rag.chunks IS 'Document chunks with vector embeddings for semantic similarity search.';

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON polly_rag.chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id
    ON polly_rag.chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_metadata
    ON polly_rag.chunks USING gin (metadata);

-- Query log for evaluation
CREATE TABLE IF NOT EXISTS polly_rag.query_log (
    id              SERIAL PRIMARY KEY,
    question        TEXT NOT NULL,
    answer          TEXT,
    source_chunks   JSONB,
    model_used      VARCHAR(100),
    latency_ms      INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly_rag.query_log IS 'Log of RAG queries for evaluation and debugging.';
