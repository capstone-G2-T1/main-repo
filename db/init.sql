-- Basic schema to prove Postgres is initialized correctly.
-- Full schema (chunks, query logs, eval history) gets extended in later stories.

CREATE TABLE IF NOT EXISTS manuals (
    id SERIAL PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year VARCHAR(4),
    language VARCHAR(5) NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
