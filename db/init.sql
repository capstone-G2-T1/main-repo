-- Vehicle Manual RAG - PostgreSQL Initial Schema
-- This file is executed automatically by Postgres Docker container on first startup.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================
-- ENUM TYPES
-- =========================

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'user');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE language_code AS ENUM ('ar', 'en');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE intent_type AS ENUM (
        'warning_light',
        'maintenance',
        'troubleshooting',
        'settings',
        'safety',
        'specification',
        'general_manual_question'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE system_variant AS ENUM (
        'baseline_vector_rag',
        'rag_normalization',
        'rag_ner_filtering',
        'rag_reranker',
        'full_system'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- =========================
-- USERS
-- =========================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- VEHICLES
-- =========================

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    trim VARCHAR(100),
    year SMALLINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT vehicles_unique_make_model_trim_year
        UNIQUE (make, model, trim, year)
);


-- =========================
-- MANUALS
-- =========================

CREATE TABLE IF NOT EXISTS manuals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    manual_name VARCHAR(255) NOT NULL,
    language language_code NOT NULL,
    checksum VARCHAR(128) NOT NULL UNIQUE,
    is_translated BOOLEAN NOT NULL DEFAULT FALSE,
    source_path TEXT,
    translated_path TEXT,
    total_pages INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- MANUAL CHUNKS
-- =========================

CREATE TABLE IF NOT EXISTS manual_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manual_id UUID NOT NULL REFERENCES manuals(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    section VARCHAR(255),
    chunk_text TEXT,
    chroma_vector_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT manual_chunks_unique_manual_chunk
        UNIQUE (manual_id, chunk_index)
);


-- =========================
-- SESSIONS
-- =========================

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    token_hash VARCHAR(255),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- QUERY LOGS
-- =========================

CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,

    raw_question TEXT NOT NULL,
    normalized_question TEXT,
    intent intent_type,

    entities JSONB,
    metadata_filter JSONB,
    retrieved_chunks JSONB,

    answer TEXT,
    citations JSONB,
    confidence VARCHAR(50),
    latency_seconds NUMERIC(10, 3),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- EVAL QUESTIONS
-- =========================

CREATE TABLE IF NOT EXISTS eval_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    manual_id UUID REFERENCES manuals(id) ON DELETE SET NULL,

    question TEXT NOT NULL,
    expected_page INTEGER,
    expected_answer_substring TEXT,
    expected_intent intent_type,
    expected_system VARCHAR(100),
    should_refuse BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- EVAL RUNS
-- =========================

CREATE TABLE IF NOT EXISTS eval_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_name VARCHAR(255) NOT NULL,
    system_variant system_variant NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =========================
-- EVAL RESULTS
-- =========================

CREATE TABLE IF NOT EXISTS eval_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eval_run_id UUID NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    eval_question_id UUID NOT NULL REFERENCES eval_questions(id) ON DELETE CASCADE,

    is_correct_retrieval BOOLEAN,
    is_grounded BOOLEAN,
    citation_accuracy BOOLEAN,
    rejection_accuracy BOOLEAN,

    recall_at_3 BOOLEAN,
    recall_at_5 BOOLEAN,
    mrr NUMERIC(10, 4),
    latency_seconds NUMERIC(10, 3),

    retrieved_pages JSONB,
    returned_citations JSONB,
    generated_answer TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT eval_results_unique_run_question
        UNIQUE (eval_run_id, eval_question_id)
);


-- =========================
-- INDEXES
-- =========================

CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_year
    ON vehicles(make, model, year);

CREATE INDEX IF NOT EXISTS idx_manuals_vehicle_id
    ON manuals(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_manuals_checksum
    ON manuals(checksum);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_manual_id
    ON manual_chunks(manual_id);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_page_number
    ON manual_chunks(page_number);

CREATE INDEX IF NOT EXISTS idx_manual_chunks_chroma_vector_id
    ON manual_chunks(chroma_vector_id);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
    ON sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_sessions_vehicle_id
    ON sessions(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_query_logs_session_id
    ON query_logs(session_id);

CREATE INDEX IF NOT EXISTS idx_query_logs_vehicle_id
    ON query_logs(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_query_logs_intent
    ON query_logs(intent);

CREATE INDEX IF NOT EXISTS idx_eval_questions_vehicle_id
    ON eval_questions(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_eval_questions_manual_id
    ON eval_questions(manual_id);

CREATE INDEX IF NOT EXISTS idx_eval_results_eval_run_id
    ON eval_results(eval_run_id);

CREATE INDEX IF NOT EXISTS idx_eval_results_eval_question_id
    ON eval_results(eval_question_id);


-- =========================
-- OPTIONAL SEED DATA
-- =========================

INSERT INTO users (email, password_hash, role)
VALUES ('demo@vehicle-rag.local', NULL, 'user')
ON CONFLICT (email) DO NOTHING;