from rag.entity_extractor import extract_entities


def test_extracts_english_vehicle_year_system_and_code():
    result = extract_entities("Battery warning P0420 in BYD Dolphin 2024")
    assert result.make == "BYD"
    assert result.model == "Dolphin"
    assert result.year == 2024
    assert result.vehicle_system == "battery"
    assert result.error_code == "P0420"


def test_extracts_normalized_arabic_system_value():
    assert extract_entities("البطاريه تحتاج فحص").vehicle_system == "battery"


def test_extracts_arabic_alias_and_warning_code():
    result = extract_entities("لمبة ABS في هافال جوليان HEV")
    assert (result.make, result.model, result.trim) == ("Haval", "Jolion", "HEV")
    assert result.vehicle_system == "brakes"
    assert result.error_code == "ABS"


def test_model_with_dot_and_partial_entities():
    result = extract_entities("ضغط إطارات فولكس فاجن ID4")
    assert (result.make, result.model) == ("Volkswagen", "ID.4")
    assert result.vehicle_system == "tires"
    assert result.year is None


def test_obd_code_is_not_a_model_and_missing_values_are_none():
    result = extract_entities("ظهر عندي الكود U0100")
    assert result.model is None
    assert result.make is None
    assert result.error_code == "U0100"


def test_empty_input_is_safe():
    assert extract_entities("").as_dict() == {
        "make": None, "model": None, "trim": None, "year": None,
        "vehicle_system": None, "error_code": None,
    }
