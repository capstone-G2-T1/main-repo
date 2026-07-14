# AI.SPIRE — G2-T1 — Dalilak

## Alpha Intelligence — ( Dalilak ) Chinese Vehicle Manual Assistant

> **Status: enhanced starter scaffold.**
> The current version runs the stack end-to-end with the core RAG flow prepared.
> Next steps: improve retrieval quality, add the full evaluation set, implement reranking, and compare system variants.

A Retrieval-Augmented Generation system for Chinese-imported vehicle manuals (BYD, GAC, Geely, MG, and similar brands).

A car owner selects their vehicle, asks a question in Arabic, and receives a grounded answer from the correct manual with a page/section citation in under 30 seconds. The system targets Arabic-speaking users and uses an **Arabic corpus** internally — English manuals are translated into Arabic during ingestion, not at query time.

---

## Project Goal

Build a local, offline-capable RAG assistant that helps Arabic-speaking drivers understand vehicle manuals by answering questions about:

- Warning lights
- Maintenance steps
- Battery and charging
- Brakes and tire pressure
- Infotainment settings
- Safety systems
- Error/warning codes
- General vehicle usage instructions

Every answer must be grounded in the retrieved manual context and include a citation (page number and manual metadata).

---

## Architecture

### Runtime request flow

```
Car owner
→ Gradio frontend
→ FastAPI backend
→ Query translation/normalization layer
→ Rule-based NER extractor
→ Intent classifier
→ Metadata filter builder
→ Chroma vector retrieval
→ Cross-encoder re-ranker
→ Ollama LLM generation
→ Grounded Arabic answer + citation
→ Query log stored in Postgres
```

### Offline ingestion pipeline

```
Raw vehicle manuals
→ Language detection
→ Translate English manuals into Arabic
→ PDF parser (pdfplumber)
→ Tesseract OCR fallback for scanned pages
→ Arabic text normalization
→ Page-aware overlapping chunking
→ Metadata extraction
→ Multilingual embedding model
→ Chunk vectors → Chroma
→ Chunk metadata → Postgres
```

---

## Corpus Language Decision

The project uses **Arabic as the locked corpus language**:

- Arabic manuals are ingested directly.
- English manuals are translated into Arabic during ingestion.
- User questions are expected in Arabic.
- Retrieval happens between Arabic user queries and Arabic manual chunks.
- No translation is performed at query time — this keeps runtime fast and retrieval stable.

**Data note:** `pdfplumber` is tried first on every page. If a page has no usable text layer, Tesseract OCR (Arabic language pack) is used as a fallback. Each chunk keeps page-aware metadata so answers can cite the exact source.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js | Simple local UI, runs in Docker |
| Backend API | FastAPI | Async, typed, easy to containerize |
| Vector Store | Chroma | Free, self-hosted, supports metadata filtering |
| Relational DB | Postgres | Manual metadata, chunk records, query logs, eval history |
| Primary Embedding | `paraphrase-multilingual-MiniLM-L12-v2` | Strong multilingual sentence embeddings, good Arabic retrieval |
| Backup Embedding | AraBERT | Optional Arabic-focused alternative |
| Re-ranker | Cross-encoder (after vector search) | Improves final ranking of retrieved chunks |
| Generation | Ollama — `qwen2.5:7b-instruct` | Fully offline, no paid API dependency |
| PDF Parsing | `pdfplumber` + Tesseract OCR (`tesseract-ocr-ara`) | Handles both digital-text and scanned PDFs |
| Translation (ingest) | Arabic translation layer | Converts English manuals into Arabic corpus |
| Query Processing | Rule-based normalization, NER, intent classifier | No model training required for MVP |
| Orchestration | Docker Compose | Consistent across machines |

---

## RAG Pipeline — Layer by Layer

### 1. Query Normalization

Prepares the user question before retrieval:

- Removes Arabic diacritics (تشكيل)
- Normalizes Arabic letter variants: `أ / إ / آ → ا`, `ى → ي`, `ة → ه`
- Maps automotive dialect/mixed terms to canonical Arabic
- Translates inline English words to Arabic equivalents

**Example:**

| | Text |
|---|---|
| User question | `لمبة battery ظهرت في BYD Dolphin شو اعمل؟` |
| Normalized | `تحذير البطارية ظهر في BYD Dolphin ما الإجراء المطلوب؟` |

---

### 2. Rule-Based NER Extractor

Extracts automotive entities from the normalized question. No model training required.

```json
{
  "make": "BYD",
  "model": "BYD Dolphin",
  "trim": null,
  "year": null,
  "system": "battery",
  "error_code": null,
  "issue_type": "warning light"
}
```

**Supported entity types:**

| Entity | Examples |
|---|---|
| Make | BYD, Changan, Geely, MG |
| Model | BYD Dolphin, Changan CS35, Geely Coolray |
| Vehicle system | brakes, battery, infotainment, tire pressure, airbag, engine |
| Error / warning code | P0420, EPB warning, TPMS warning |
| Issue type | warning light, maintenance, safety, settings, troubleshooting |

---

### 3. Intent Classifier

Rule-based in the MVP — no training required.

| Intent | Meaning |
|---|---|
| `warning_light` | User asks about a warning symbol or light |
| `maintenance` | User asks about service or maintenance steps |
| `troubleshooting` | User has a problem and wants a fix |
| `settings` | User asks how to change a vehicle setting |
| `safety` | User asks about safety systems or warnings |
| `specification` | User asks about values (tire pressure, battery info) |
| `general_manual_question` | General question from the manual |

---

### 4. Metadata Filtering

Every chunk carries structured metadata. The retriever applies hard filters to prevent cross-model leakage (retrieving the wrong car's manual):

```json
{
  "make": "BYD",
  "model": "Dolphin",
  "trim": "Standard",
  "year": "2024",
  "page": 52,
  "language": "ar",
  "manual_name": "BYD_Dolphin_2024_AR.pdf",
  "section": "Battery warning indicators"
}
```

---

### 5. Cross-Encoder Re-ranker

After Chroma returns candidate chunks, a cross-encoder scores each query/chunk pair more carefully:

```
Vector search retrieves top 10 chunks
→ Cross-encoder re-ranks them
→ Top 3 chunks sent to the LLM
```

A pretrained cross-encoder is used in the MVP. Fine-tuning is optional for later.

---

### 6. Grounded Answer Generation

The LLM receives only the selected manual chunks and must:

- Answer in Arabic
- Use only the retrieved context
- Cite the source page
- Say "not found in the manual" if the context is insufficient
- Never guess

**Example output:**
```
حسب كتيب BYD Dolphin صفحة 52، ظهور تحذير البطارية يعني أن نظام البطارية يحتاج إلى فحص.
ينصح بإيقاف السيارة في مكان آمن والتواصل مع مركز الصيانة إذا استمر التحذير.
المصدر: BYD Dolphin 2024 Manual, page 52.
```

---

## Running the Project

### 1. Copy the environment file

```bash
cp .env.example .env
```

### 2. Add vehicle manuals

Place PDFs inside `data/raw_manuals/`. The ingestion pipeline handles language detection and translation automatically.

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Pull the local LLM *(first run only)*

```bash
docker compose exec ollama ollama pull qwen2.5:7b-instruct
```

### 5. Run ingestion

```bash
docker compose exec backend bash scripts/run_ingestion.sh
```

The ingestion pipeline will:

1. Read PDFs from `data/raw_manuals/`
2. Detect language
3. Translate English manuals into Arabic
4. Extract text using `pdfplumber`
5. Use Tesseract OCR for scanned pages
6. Normalize Arabic text
7. Chunk pages with overlap
8. Attach metadata to every chunk
9. Embed chunks
10. Store vectors in Chroma
11. Store metadata in Postgres

### 6. Open the UI

| Service | URL |
|---|---|
| Frontend  | http://localhost:3001 |
| Backend API docs | http://localhost:8000/docs |

---

## API Reference

### `POST /ask`

**Request:**
```json
{
  "question": "ظهرت لمبة البطارية في BYD Dolphin شو أعمل؟",
  "selected_vehicle": "BYD Dolphin"
}
```

**Internal processing:**
```json
{
  "normalized_query": "تحذير البطارية ظهر في BYD Dolphin ما الإجراء المطلوب؟",
  "entities": { "make": "BYD", "model": "Dolphin", "system": "battery", "issue_type": "warning_light" },
  "intent": "warning_light",
  "metadata_filter": { "make": "BYD", "model": "Dolphin" }
}
```

**Response:**
```json
{
  "answer": "حسب كتيب BYD Dolphin، ظهور تحذير البطارية يعني أن نظام البطارية يحتاج إلى فحص...",
  "citations": [
    { "manual_name": "BYD_Dolphin_2024_AR.pdf", "page": 52, "section": "Battery warning indicators" }
  ],
  "confidence": "medium"
}
```

---

## Evaluation Plan

The evaluation compares multiple system versions — not just a working demo, but measurable improvement:

| System Variant | Expected Result |
|---|---|
| Baseline RAG (no normalization/translation) | Sometimes fails on Arabic dialect queries |
| RAG + query normalization | Better match between user question and manual text |
| RAG + NER + metadata filtering | Accurate retrieval from the correct vehicle/section |
| RAG + citation | Trustworthy, grounded answers |
| RAG + cross-encoder re-ranker | Fewer irrelevant chunks in final context |

### Evaluation dataset format

```json
{
  "question": "كيف أضبط ضغط الإطارات في Changan CS35؟",
  "manual": "Changan_CS35_2023_AR.pdf",
  "make": "Changan",
  "model": "CS35",
  "expected_page": 84,
  "expected_answer_substring": "ضغط الإطارات",
  "intent": "specification",
  "system": "tire_pressure"
}
```

### Metrics

| Metric | Meaning |
|---|---|
| Recall@K | Did the correct chunk/page appear in the top K results? |
| MRR | How high was the first correct result ranked? |
| Grounded Rate | Did the answer stay faithful to the retrieved context? |
| Citation Accuracy | Did the answer cite the correct manual/page? |
| Rejection Accuracy | Did the system refuse when the answer was not in the manual? |
| Latency | Did the system answer within the 30-second target? |

### Baselines

- TF-IDF retrieval
- BM25 retrieval
- Plain vector RAG
- Vector RAG + query normalization
- Vector RAG + NER filtering
- Vector RAG + NER filtering + cross-encoder re-ranking

---

## Roadmap

- [ ] Full 50+ question held-out evaluation set
- [ ] `scripts/run_eval.py` — automated evaluation harness
- [ ] Query normalization tests
- [ ] Rule-based NER extractor implementation
- [ ] Rule-based intent classifier implementation
- [ ] Metadata filter builder
- [ ] Cross-encoder re-ranker after vector retrieval
- [ ] BM25 and TF-IDF baseline comparison
- [ ] Grounded-answer rejection logic
- [ ] Citation accuracy scoring
- [ ] OCR quality spot-check report (review `ocr_page_count` manuals)
- [ ] GitHub Actions CI — lint + pytest
- [ ] Replace `db/init.sql` with Alembic migrations
