"""Build Chroma filters from authoritative UI selection and extracted entities."""

from __future__ import annotations

import re

from rag.entity_extractor import extract_entities
from rag.types import ExtractedEntities


METADATA_ALIASES = {
    "make": {
        "BYD": ("BYD", "Byd"),
        "Byd": ("BYD", "Byd"),
        "Volkswagen": ("Volkswagen", "VW", "Vw"),
        "VW": ("Volkswagen", "VW", "Vw"),
        "Vw": ("Volkswagen", "VW", "Vw"),
        "Geely": ("Geely", "GEELY"),
        "GEELY": ("Geely", "GEELY"),
    },
    "model": {
        "Dolphin": ("Dolphin", "DOLPHIN"),
        "Seagull": ("Seagull", "SEAGULL"),
        "SEAGULL": ("Seagull", "SEAGULL"),
        "ID.4": ("ID.4", "ID4"),
        "ID4": ("ID.4", "ID4"),
        "MK Series": ("MK",),
        "MK": ("MK",),
    },
}

INDEXED_FILTER_FIELDS = {"make", "model"}


def _alias_key(value: str) -> str:
    return re.sub(r"[\s._-]+", "", value.casefold())


def _lookup_aliases(field: str, value: str) -> tuple[str, ...]:
    aliases = METADATA_ALIASES.get(field, {})
    wanted = _alias_key(value)
    for canonical, candidates in aliases.items():
        if wanted == _alias_key(canonical) or wanted in {_alias_key(candidate) for candidate in candidates}:
            return candidates
    return (value,)


def _metadata_condition(field: str, value: str) -> dict:
    values = _lookup_aliases(field, value)
    return {field: {"$in": list(values)}}


def _selected_entities(selected_vehicle: str | None) -> ExtractedEntities:
    return extract_entities(selected_vehicle or "")


def resolve_vehicle(
    selected_vehicle: str | None,
    entities: ExtractedEntities,
) -> ExtractedEntities:
    """Resolve vehicle identity with UI selection overriding question NER values."""
    selected = _selected_entities(selected_vehicle)
    make = selected.make or entities.make
    model = selected.model or entities.model
    if selected.make and selected.model:
        make, model = selected.make, selected.model
    return ExtractedEntities(
        make=make,
        model=model,
        trim=selected.trim or entities.trim,
        year=selected.year or entities.year,
        vehicle_system=entities.vehicle_system,
        error_code=entities.error_code,
    )


def build_metadata_filter(
    selected_vehicle: str | None,
    entities: ExtractedEntities,
) -> dict:
    """Return valid Chroma ``where`` syntax using ingestion metadata names."""
    resolved = resolve_vehicle(selected_vehicle, entities)
    conditions: list[dict] = []
    if resolved.make and "make" in INDEXED_FILTER_FIELDS:
        conditions.append(_metadata_condition("make", resolved.make))
    if resolved.model and "model" in INDEXED_FILTER_FIELDS:
        conditions.append(_metadata_condition("model", resolved.model))

    if not conditions:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}
