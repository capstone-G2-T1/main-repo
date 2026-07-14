from rag.entity_extractor import extract_entities
from rag.metadata_filter import build_metadata_filter, resolve_vehicle


def test_complete_ui_selection_is_authoritative_without_year_filter():
    ner = extract_entities("Geely Geometry C 2023")
    resolved = resolve_vehicle("BYD Dolphin 2024", ner)
    assert (resolved.make, resolved.model, resolved.year) == ("BYD", "Dolphin", 2024)
    assert build_metadata_filter("BYD Dolphin 2024", ner) == {
        "$and": [
            {"make": {"$in": ["BYD", "Byd"]}},
            {"model": {"$in": ["Dolphin", "DOLPHIN"]}},
        ]
    }


def test_partial_ui_uses_ner_for_missing_fields():
    result = resolve_vehicle("BYD", extract_entities("Dolphin 2024"))
    assert (result.make, result.model, result.year) == ("BYD", "Dolphin", 2024)


def test_ner_only_and_missing_metadata():
    assert build_metadata_filter(None, extract_entities("Haval Jolion")) == {
        "$and": [{"make": {"$in": ["Haval"]}}, {"model": {"$in": ["Jolion"]}}]
    }
    assert build_metadata_filter(None, extract_entities("شو المشكلة؟")) == {}


def test_volkswagen_alias_filters_include_make_and_model():
    expected = {
        "$and": [
            {"make": {"$in": ["Volkswagen", "VW", "Vw"]}},
            {"model": {"$in": ["ID.4", "ID4"]}},
        ]
    }
    assert build_metadata_filter("Vw ID4", extract_entities("")) == expected
    assert build_metadata_filter("Volkswagen ID.4", extract_entities("")) == expected
    assert build_metadata_filter("VW ID4", extract_entities("")) == expected


def test_byd_alias_filters_include_make_and_model():
    expected = {
        "$and": [
            {"make": {"$in": ["BYD", "Byd"]}},
            {"model": {"$in": ["Seagull", "SEAGULL"]}},
        ]
    }
    assert build_metadata_filter("Byd SEAGULL", extract_entities("")) == expected
    assert build_metadata_filter("BYD Seagull", extract_entities("")) == expected


def test_make_only_filter_does_not_use_single_item_and():
    assert build_metadata_filter("BYD", extract_entities("")) == {"make": {"$in": ["BYD", "Byd"]}}


def test_geely_alias_filters_include_make_and_model():
    expected = {
        "$and": [
            {"make": {"$in": ["Geely", "GEELY"]}},
            {"model": {"$in": ["MK"]}},
        ]
    }
    assert build_metadata_filter("Geely MK", extract_entities("")) == expected
    assert build_metadata_filter("GEELY MK", extract_entities("")) == expected


def test_selected_vehicle_beats_conflicting_ner_and_no_year_filter():
    where = build_metadata_filter("VW ID4", extract_entities("BYD Seagull 2024"))
    assert where == {
        "$and": [
            {"make": {"$in": ["Volkswagen", "VW", "Vw"]}},
            {"model": {"$in": ["ID.4", "ID4"]}},
        ]
    }
    assert "year" not in str(where)
