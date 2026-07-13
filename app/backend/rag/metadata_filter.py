"""Build Chroma filters from authoritative UI selection and extracted entities."""

from __future__ import annotations

from rag.entity_extractor import extract_entities
from rag.types import ExtractedEntities


METADATA_ALIASES = {
    "make": {
        "BYD": ("BYD", "Byd"),
        "Volkswagen": ("Volkswagen", "VW", "Vw"),
        "VW": ("Volkswagen", "VW", "Vw"),
    },
    "model": {
        "Dolphin": ("Dolphin", "DOLPHIN"),
        "Seagull": ("Seagull", "SEAGULL"),
        "ID.4": ("ID.4", "ID4"),
        "MK Series": ("MK Series", "MK"),
    },
}


def _metadata_condition(field: str, value: str) -> dict:
    values = METADATA_ALIASES.get(field, {}).get(value, (value,))
    if len(values) == 1:
        return {field: {"$eq": values[0]}}
    return {field: {"$in": list(values)}}


def _selected_entities(selected_vehicle: str | None) -> ExtractedEntities:
    return extract_entities(selected_vehicle or "")


def resolve_vehicle(
    selected_vehicle: str | None,
    entities: ExtractedEntities,
) -> ExtractedEntities:
    """Resolve vehicle identity with UI selection overriding question NER values."""
    selected = _selected_entities(selected_vehicle)
    return ExtractedEntities(
        make=selected.make or entities.make,
        model=selected.model or entities.model,
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
    if resolved.make:
        conditions.append(_metadata_condition("make", resolved.make))
    if resolved.model:
        conditions.append(_metadata_condition("model", resolved.model))
    if resolved.year is not None:
        # Ingestion stores the year as a string in Chroma metadata.
        conditions.append({"year": {"$eq": str(resolved.year)}})

    if not conditions:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}
