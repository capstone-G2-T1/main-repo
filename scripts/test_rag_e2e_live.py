"""
Live end-to-end smoke test for the RAG pipeline.

Unlike tests/test_rag_pipeline.py, tests/test_retriever.py, and tests/test_generator.py
(which mock Chroma and Ollama), this script hits the real, running services:
Chroma at localhost:8001 and Ollama at localhost:11434. It embeds and inserts one sample
Arabic chunk, retrieves it for a matching question, and generates a grounded answer.

Not a pytest test (no assertions) -- run it directly so its prints are visible:

    python scripts/test_rag_e2e_live.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Windows consoles default to cp1252, which can't encode Arabic output.
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for path in (str(BACKEND), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

# This runs on the host, not inside the compose network, so it needs the
# host-published ports/names rather than the in-network service names from .env.
os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
# qwen2.5:3b-instruct isn't pulled in the ollama container (only qwen2.5:7b-instruct is,
# see docker-compose.yml) -- reuse what's already there instead of pulling a new model.
os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:7b-instruct")
# CPU-only inference on a 7B model is slow, especially on a cold first load; the app's
# default 25s (see .env / core/config.py) is tuned for a warm/GPU setup, not this smoke test.
os.environ.setdefault("OLLAMA_TIMEOUT_SECONDS", "180")
# Isolated collection so this smoke test never touches real manual data in vehicle_manuals_ar.
os.environ.setdefault("CHROMA_COLLECTION_NAME", "e2e_smoke_test")
os.environ["DEBUG"] = "false"

from core.config import settings  # noqa: E402
from ingestion.embedder import embed_texts  # noqa: E402
from ingestion.vector_store import CHROMA_COLLECTION_NAME, _get_client, upsert_chunks  # noqa: E402
from rag.generator import generate_answer  # noqa: E402
from rag.retriever import retrieve_chunks  # noqa: E402
from rag.types import ExtractedEntities  # noqa: E402

SAMPLE_ID = "e2e_smoke:0"
SAMPLE_TEXT = (
    "يجب فحص ضغط الإطارات كل شهر. الضغط الموصى به هو 33 رطل لكل بوصة مربعة "
    "(psi) للإطارات الأمامية والخلفية."
)
SAMPLE_METADATA = {
    "manual_name": "e2e_smoke_test.pdf",
    "make": "BYD",
    "model": "Dolphin",
    "year": "2024",
    "page": 1,
    "section": "Tires",
}
QUESTION = "ما هو ضغط الإطارات الموصى به؟"


def main() -> None:
    print(f"Chroma:  {os.environ['CHROMA_HOST']}:{os.environ['CHROMA_PORT']} (collection={CHROMA_COLLECTION_NAME})")
    print(f"Ollama:  {settings.OLLAMA_HOST} (model={settings.OLLAMA_MODEL})")
    print()

    print("1. Embedding + inserting sample chunk into Chroma...")
    vectors = embed_texts([SAMPLE_TEXT])
    upsert_chunks([SAMPLE_ID], vectors, [SAMPLE_TEXT], [SAMPLE_METADATA])
    print(f"   Inserted id={SAMPLE_ID!r} text={SAMPLE_TEXT!r}\n")

    print(f"2. Retrieving chunks for question: {QUESTION!r}")
    chunks = retrieve_chunks(QUESTION, top_k=3)
    if not chunks:
        print("   No chunks retrieved -- aborting.")
        return
    for chunk in chunks:
        print(f"   - id={chunk.id} score={chunk.retrieval_score} page={chunk.metadata.get('page')} text={chunk.text!r}")
    print()

    print("3. Generating grounded answer with Ollama...")
    answer, citations = generate_answer(
        QUESTION,
        QUESTION,
        ExtractedEntities(make="BYD", model="Dolphin"),
        "specification",
        "BYD Dolphin 2024",
        chunks,
    )
    print(f"   Answer:\n{answer}\n")
    print(f"   Citations: {citations}\n")

    print("4. Cleaning up smoke-test collection...")
    try:
        _get_client().delete_collection(CHROMA_COLLECTION_NAME)
        print(f"   Deleted collection {CHROMA_COLLECTION_NAME!r}")
    except Exception as exc:  # best-effort cleanup only
        print(f"   Cleanup skipped: {exc.__class__.__name__}: {exc}")


if __name__ == "__main__":
    main()
