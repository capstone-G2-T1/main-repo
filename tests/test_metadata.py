from rag.metadata import canonical_manual_name, canonicalize_metadata


def test_metadata_canonicalization_maps_page_and_section_aliases():
    metadata = canonicalize_metadata(
        {
            "manual_name": "Volkswagen ID.4.pdf",
            "page_number": "12",
            "section_title": "Lights",
            "year": None,
        }
    )
    assert metadata["manual_name"] == "VW_ID4"
    assert metadata["page"] == 12
    assert metadata["section"] == "Lights"
    assert metadata["year"] is None


def test_manual_aliases():
    assert canonical_manual_name("BYD SEAGULL") == "BYD_SEAGULL"
    assert canonical_manual_name("GEELY_MK_SERIES.pdf") == "GEELY_MK"
    assert canonical_manual_name(None) is None
