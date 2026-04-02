-- POLLY Hierarchical RAG Schema — brand new schema, zero changes to polly_rag.*
-- Run: psql $DB_URL -f sql/004_hierarchical_rag_schema.sql

CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS polly_rag_hierarchical;

-- ---------------------------------------------------------------------------
-- polly_rag_hierarchical.documents
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS polly_rag_hierarchical.documents (
    id                      SERIAL PRIMARY KEY,
    filename                VARCHAR(500) NOT NULL,
    file_type               VARCHAR(20)  NOT NULL,
    title                   VARCHAR(500),
    file_size_bytes         INTEGER,
    markdown_text           TEXT,
    chunk_count             INTEGER      DEFAULT 0,
    product_id              INTEGER      REFERENCES polly.products(id) ON DELETE SET NULL,
    doc_type                VARCHAR(50),
    compliance_document_id  INTEGER      REFERENCES polly.compliance_documents(id) ON DELETE SET NULL,
    approved                BOOLEAN      DEFAULT FALSE,
    approved_by             INTEGER      REFERENCES polly.users(id) ON DELETE SET NULL,
    approved_at             TIMESTAMPTZ,
    jurisdiction            VARCHAR(20)  DEFAULT 'UK',
    processed_at            TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE(filename)
);

CREATE INDEX IF NOT EXISTS idx_h_documents_product_id  ON polly_rag_hierarchical.documents(product_id);
CREATE INDEX IF NOT EXISTS idx_h_documents_doc_type    ON polly_rag_hierarchical.documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_h_documents_approved    ON polly_rag_hierarchical.documents(approved);

-- ---------------------------------------------------------------------------
-- polly_rag_hierarchical.chunks
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS polly_rag_hierarchical.chunks (
    id              SERIAL PRIMARY KEY,
    document_id     INTEGER      NOT NULL REFERENCES polly_rag_hierarchical.documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER      NOT NULL,
    content         TEXT         NOT NULL,   -- small child text — embedded + matched
    parent_section  TEXT,                    -- full section text — sent to LLM
    section_name    TEXT,                    -- e.g. "Section 8: Risk Factors"
    product_id      INTEGER      REFERENCES polly.products(id) ON DELETE SET NULL,
    doc_type        VARCHAR(50),
    approved        BOOLEAN      DEFAULT FALSE,
    jurisdiction    VARCHAR(20)  DEFAULT 'UK',
    token_count     INTEGER,
    metadata        JSONB        DEFAULT '{}',
    embedding       vector(384),
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_h_chunks_embedding
    ON polly_rag_hierarchical.chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_h_chunks_filter
    ON polly_rag_hierarchical.chunks(product_id, doc_type, approved);

CREATE INDEX IF NOT EXISTS idx_h_chunks_document_id
    ON polly_rag_hierarchical.chunks(document_id);

-- ---------------------------------------------------------------------------
-- polly_rag_hierarchical.query_log
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS polly_rag_hierarchical.query_log (
    id            SERIAL PRIMARY KEY,
    question      TEXT    NOT NULL,
    answer        TEXT,
    source_chunks JSONB,
    model_used    VARCHAR(100),
    product_id    INTEGER REFERENCES polly.products(id) ON DELETE SET NULL,
    doc_types     TEXT[],
    latency_ms    INTEGER,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
