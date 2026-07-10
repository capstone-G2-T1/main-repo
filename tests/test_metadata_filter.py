from rag.entity_extractor import extract_entities
from rag.metadata_filter import build_metadata_filter, resolve_vehicle


def test_complete_ui_selection_is_authoritative():
    ner = extract_entities("Geely Geometry C 2023")
    resolved = resolve_vehicle("BYD Dolphin 2024", ner)
    assert (resolved.make, resolved.model, resolved.year) == ("BYD", "Dolphin", 2024)
    assert build_metadata_filter("BYD Dolphin 2024", ner) == {
        "$and": [
            {"make": {"$eq": "BYD"}},
            {"model": {"$eq": "Dolphin"}},
            {"year": {"$eq": "2024"}},
        ]
    }


def test_partial_ui_uses_ner_for_missing_fields():
    result = resolve_vehicle("BYD", extract_entities("Dolphin 2024"))
    assert (result.make, result.model, result.year) == ("BYD", "Dolphin", 2024)


def test_ner_only_and_missing_metadata():
    assert build_metadata_filter(None, extract_entities("Haval Jolion")) == {
        "$and": [{"make": {"$eq": "Haval"}}, {"model": {"$eq": "Jolion"}}]
    }
    assert build_metadata_filter(None, extract_entities("شو المشكلة؟")) == {}
