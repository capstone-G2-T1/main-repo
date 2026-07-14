import pytest

from rag.query_normalizer import normalize_query


def test_normalization_preserves_technical_tokens():
    text = normalize_query("READY TPMS P0420 ID.4 BYD")
    assert "READY" in text
    assert "TPMS" in text
    assert "P0420" in text
    assert "ID.4" in text
    assert "BYD" in text


def test_arabic_diacritics_tatweel_and_whitespace_are_removed():
    assert normalize_query(" السَّــــلام   عليكم ") == "السلام عليكم"


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        normalize_query("   ")
