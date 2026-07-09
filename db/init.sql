-- =============================================================
-- AI.SPIRE G2-T1 — Vehicle Manual RAG
-- Database initialization script
-- =============================================================

-- -------------------------------------------------------------
-- Table: query_logs
-- Stores every /ask request with full pipeline output for
-- debugging, evaluation, and demo evidence.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_logs (
    id                       SERIAL PRIMARY KEY,

    -- User input
    original_question        TEXT        NOT NULL,
    selected_vehicle         TEXT        NOT NULL,

    -- Pipeline intermediate outputs
    normalized_question      TEXT,
    ner_entities             JSONB,
    intent                   TEXT,
    metadata_filter          JSONB,

    -- Retrieval summary: metadata + first 200 chars of each chunk
    -- Nullable — pipeline may return empty results without crashing
    retrieved_chunks_summary JSONB,

    -- Final output
    answer                   TEXT,
    citations                JSONB,
    confidence               TEXT,

    -- Performance
    latency_seconds          FLOAT,

    -- Audit
    created_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast recent-logs queries
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at
    ON query_logs (created_at DESC);

-- Index for filtering by vehicle
CREATE INDEX IF NOT EXISTS idx_query_logs_selected_vehicle
    ON query_logs (selected_vehicle);