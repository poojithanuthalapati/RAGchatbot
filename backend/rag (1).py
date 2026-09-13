-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Stores chunked, embedded source documents (the RAG knowledge base)
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,              -- e.g. filename or upload label
    chunk_index INT NOT NULL,          -- order of chunk within source doc
    content TEXT NOT NULL,             -- raw chunk text
    embedding VECTOR(384) NOT NULL,    -- all-MiniLM-L6-v2 dimension
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Speeds up similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Stores chat turns so you can review/debug retrieval quality later
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    retrieved_doc_ids BIGINT[],        -- which document chunks were used to answer
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chat_history_session_idx ON chat_history (session_id);

-- ============================================================
-- Resume-vs-job-description analyzer tables
-- ============================================================

CREATE TABLE IF NOT EXISTS resumes (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    filename TEXT,
    raw_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resume_chunks (
    id BIGSERIAL PRIMARY KEY,
    resume_id BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS resume_chunks_resume_idx ON resume_chunks (resume_id);

CREATE TABLE IF NOT EXISTS job_postings (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT,
    raw_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS job_posting_chunks (
    id BIGSERIAL PRIMARY KEY,
    job_posting_id BIGINT NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS job_posting_chunks_jp_idx ON job_posting_chunks (job_posting_id);

-- One row per resume-vs-JD comparison. This is the table the future
-- Snowflake analytics pipeline will read from.
CREATE TABLE IF NOT EXISTS analyses (
    id BIGSERIAL PRIMARY KEY,
    resume_id BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_posting_id BIGINT NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    overall_score NUMERIC(5,2) NOT NULL,      -- 0-100 similarity score
    weak_resume_chunks JSONB,                  -- resume bullets that matched poorly
    uncovered_jd_chunks JSONB,                 -- JD requirements the resume doesn't cover well
    suggestions JSONB,                          -- LLM-generated rewrite suggestions
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS analyses_resume_idx ON analyses (resume_id);
CREATE INDEX IF NOT EXISTS analyses_job_posting_idx ON analyses (job_posting_id);
