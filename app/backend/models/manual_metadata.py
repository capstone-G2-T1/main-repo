"""
models/manual_metadata.py

Data model for a single vehicle manual's metadata, as produced by
the ingestion loader (app/backend/ingestion/manual_loader.py).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ManualMetadata:
    """Structured metadata returned for every manual found."""
    make: str
    model: str
    year: Optional[str]
    file_path: str