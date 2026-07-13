"""
Runs the real, unmodified ingestion entrypoint (app/backend/ingestion/run_ingestion.py:
run_ingestion_for_directory) against data/raw_manuals from the host, pointed at the
docker-compose services via their published ports instead of the in-network service names.

    python scripts/run_full_ingestion.py
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for path in (str(BACKEND), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:7b-instruct")
os.environ["DEBUG"] = "false"

from ingestion.run_ingestion import run_ingestion_for_directory  # noqa: E402

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    summaries = run_ingestion_for_directory(str(ROOT / "data" / "raw_manuals"))
    print("\n=== Ingestion summary ===")
    for s in summaries:
        print(
            f"{s.manual_name}: skipped={s.skipped} reason={s.reason} "
            f"chunk_count={s.chunk_count} vehicle_id={s.vehicle_id} manual_id={s.manual_id}"
        )
