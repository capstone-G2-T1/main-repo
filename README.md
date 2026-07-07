# AI.SPIRE — G2-T1 — Vehicle Manual RAG (Alpha Intelligence)

> Status: **starter scaffold**. This gets the stack running end-to-end with
> stub logic in place; retrieval quality, prompt tuning, and the full 50+
> question eval set are next steps .

Retrieval-augmented Q&A over Chinese-imported vehicle manuals (BYD, Changan,
and similar), sourced as **Arabic-ready PDFs** (see Data note below). A user
picks their vehicle, asks a question in Arabic, and gets a grounded answer
with a page/section citation in under 30 seconds.

## Architecture

**Runtime (online) request flow:**
Car owner → Gradio frontend → FastAPI backend → Arabic text normalizer →
Chroma vector retrieval (filtered by vehicle model) → Ollama LLM generation
(grounded, low temperature) → answer + citation back to the user. Every
exchange is logged to Postgres.

**Offline ingestion pipeline:**
Raw manual PDFs (Arabic, a mix of digital text and scanned pages) → PDF
parser (`pdfplumber`, with a Tesseract OCR fallback for scanned pages) →
page-aware overlapping chunker → multilingual embedder
(`sentence-transformers`) → chunk vectors stored in Chroma, chunk + manual
metadata stored in Postgres.

**Data note:** manuals are ingested as Arabic PDFs, not machine-translated
at query time. Since the source PDFs are a known mix of digitally-generated
and scanned documents, `pdf_parser.py` tries `pdfplumber` text extraction
first and only falls back to OCR (Tesseract, Arabic language pack) on pages
where that comes back empty or near-empty -- keeping ingestion fast for the
text-native majority while still handling scanned pages without a manual
sorting step.


## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Gradio |Runs locally in Docker |
| Backend API | FastAPI | Async, typed, easy to containerize |
| Vector store | Chroma | Free, self-hosted, simple filtered search |
| Relational DB | Postgres | Manual/chunk metadata, query logs, eval run history |
| Embeddings | `sentence-transformers` (multilingual, e.g. `intfloat/multilingual-e5-base`) | Manuals and questions are both Arabic (same-language retrieval); kept multilingual over Arabic-only because it's specifically benchmarked on Arabic (MIRACL) and better-supported — swappable via `.env`, no code change |
| Generation | Ollama (local LLM, e.g. `qwen2.5:7b-instruct`) | Runs fully offline |
| PDF parsing | `pdfplumber` + Tesseract OCR fallback (`tesseract-ocr-ara`) | Manuals are a mix of digital-text and scanned PDFs; OCR only runs on pages with no usable text layer |
| Orchestration | Docker Compose | Docker packages the application and all its dependencies into a portable container so it runs consistently on any machine  |

## Directory structure

```
aispire-g2t1/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── db/
│   └── init.sql              # Postgres schema (manuals, chunks, queries, eval_runs)
├── app/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── api/routes.py     # /ask, /health
│   │   ├── core/config.py    # env-driven settings
│   │   ├── db/                # SQLAlchemy models + session
│   │   ├── rag/                # normalizer, retriever, generator, embeddings
│   │   └── ingestion/          # pdf_parser, chunker, run_ingestion.py
│   └── frontend/
│       ├── Dockerfile
│       └── gradio_app.py     # thin UI, calls backend over HTTP
├── data/
│   ├── raw_manuals/           # source PDFs
│   ├── processed_chunks/
│   └── eval/
│       └── test_questions.sample.json
├── scripts/
│   └── run_ingestion.sh
└── tests/
    └── test_chunker.py
```

## Running it

1. Copy the environment file and adjust if needed:
   ```
   cp .env.example .env
   ```
2. Drop 2-5 manufacturer PDFs into `data/raw_manuals/` .

3. Start the stack:
   ```
   docker compose up --build
   ```
4. Pull the local LLM into the Ollama container (first run only):
   ```
   docker compose exec ollama ollama pull qwen2.5:7b-instruct
   ```
5. Run ingestion for each manual. Each PDF is parsed page-by-page; any page
   with no usable text layer is OCR'd automatically, and the script prints
   how many pages that affected so you can spot-check them:
   ```
   docker compose exec backend bash scripts/run_ingestion.sh
   ```
   Manuals default to `--language ar`; pass `--language zh` for the rare
   Chinese-only manual if one shows up in the data set.
6. Open the UI at `http://localhost:7860`. Backend API docs at
   `http://localhost:8000/docs`.

## Evaluation

`data/eval/test_questions.sample.json` shows the expected format (question,
manual, expected page, expected answer substring) from the proposal's
evaluation plan. It currently holds 3 sample questions; the full 50+
hand-validated set is a Day 1-2 task. Baselines to compare against: TF-IDF, BM25. Primary
metrics: Recall@K and grounded rate, averaged over 3 seeded runs.

## Roadmap / not yet implemented

- [ ] Full 50+ question held-out eval set + `scripts/run_eval.py`
- [ ] Grounded-answer rejection logic (reject if key phrases absent from
      retrieved context) referenced in the risk table
- [ ] BM25/TF-IDF baseline comparison harness
- [ ] OCR quality spot-check once real scanned manuals arrive (Tesseract's
      Arabic accuracy is decent but not perfect on low-resolution scans --
      worth a manual review pass on the `ocr_page_count` manuals before
      trusting those chunks in eval)
- [ ] Automated Alembic migrations (currently a single `db/init.sql`)
- [ ] CI (lint + `pytest`) via GitHub Actions