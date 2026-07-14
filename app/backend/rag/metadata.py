"""Shared metadata normalization for retrieved manual chunks and eval."""

from __future__ import annotations

from typing import Any


MANUAL_ALIASES = {
    "VW_ID4": "VW_ID4",
    "VW ID4": "VW_ID4",
    "VOLKSWAGEN_ID4": "VW_ID4",
    "VOLKSWAGEN ID4": "VW_ID4",
    "VOLKSWAGEN_ID.4": "VW_ID4",
    "VOLKSWAGEN ID.4": "VW_ID4",
    "BYD_SEAGULL": "BYD_SEAGULL",
    "BYD SEAGULL": "BYD_SEAGULL",
    "GEELY_MK": "GEELY_MK",
    "GEELY MK": "GEELY_MK",
    "GEELY_MK_SERIES": "GEELY_MK",
    "GEELY MK SERIES": "GEELY_MK",
}


def _int_or_original(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return value


def canonical_manual_name(value: Any) -> str | None:
    """Return canonical manual identifier for known indexed manuals."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    stem = text.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].rsplit(".", 1)[0]
    key = " ".join(stem.replace("-", " ").replace("_", " ").upper().split())
    return MANUAL_ALIASES.get(key, MANUAL_ALIASES.get(key.replace(" ", "_"), stem))


def canonicalize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Map alternate metadata keys to one stable shape without stringifying None."""
    if not isinstance(metadata, dict):
        return {}
    canonical = dict(metadata)
    if canonical.get("page") is None and canonical.get("page_number") is not None:
        canonical["page"] = canonical.get("page_number")
    if canonical.get("section") is None and canonical.get("section_title") is not None:
        canonical["section"] = canonical.get("section_title")
    if "page" in canonical:
        canonical["page"] = _int_or_original(canonical.get("page"))
    manual = canonical_manual_name(canonical.get("manual_name"))
    if manual is not None:
        canonical["manual_name"] = manual
    for key in ("make", "model", "year", "manual_name", "language", "section"):
        if key in canonical and canonical[key] is None:
            canonical[key] = None
    return canonical


def chunk_stable_id(chunk_id: Any, text: str, metadata: dict[str, Any] | None) -> str:
    """Prefer Chroma IDs, falling back to manual/page/section/text identity."""
    if chunk_id is not None and str(chunk_id).strip():
        return str(chunk_id)
    meta = canonicalize_metadata(metadata)
    return "|".join(
        [
            str(meta.get("manual_name") or ""),
            str(meta.get("page") or ""),
            str(meta.get("section") or ""),
            text[:120],
        ]
    )
