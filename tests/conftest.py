"""Test path setup matching the backend container's /app layout."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"

# Root comes first so ``db`` always resolves to the canonical root package.
for path in (str(BACKEND), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ["DEBUG"] = "false"
