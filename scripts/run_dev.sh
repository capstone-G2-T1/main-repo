#!/usr/bin/env bash
#
# Local (non-Docker) dev runner for the FastAPI backend, for git bash on Windows.
#
# Why this exists:
#   docker-compose.yml mounts the repo-root `db/` folder into the backend
#   container at /app/db, alongside the app/backend code mounted at /app.
#   That merge is what lets `from db.models import ...` resolve inside
#   Docker. Running `uvicorn` directly from app/backend on your host
#   doesn't get that merge, so `db` isn't importable unless we put the
#   repo root on PYTHONPATH ourselves.
#
# Usage (from anywhere, run with bash):
#   bash scripts/run_dev.sh            # defaults to port 8000
#   bash scripts/run_dev.sh 8080       # custom port, e.g. to dodge a
#                                       # Windows excluded port range
#
# If you still hit WinError 10013 on the default port, check Windows'
# reserved port ranges from git bash with:
#   netsh.exe interface ipv4 show excludedportrange protocol=tcp
# and pick a port outside the listed ranges.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/app/backend"
PORT="${1:-8000}"

if [ ! -d "$BACKEND_DIR" ]; then
  echo "Expected backend at $BACKEND_DIR — run this from the repo, folder layout looks off." >&2
  exit 1
fi

# Repo root -> makes `db.*` importable.
# app/backend -> makes `api.*`, `core.*`, `rag.*`, `ingestion.*` importable.
export PYTHONPATH="$REPO_ROOT:$BACKEND_DIR"

cd "$REPO_ROOT"

echo "Starting backend on http://127.0.0.1:$PORT (docs at /docs)"
uvicorn main:app \
  --app-dir "$BACKEND_DIR" \
  --reload \
  --host 127.0.0.1 \
  --port "$PORT"
