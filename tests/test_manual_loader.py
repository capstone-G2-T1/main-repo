from manual_loader import load_manuals


def test_load_manuals_serializes_pydantic_metadata(tmp_path):
    manual = tmp_path / "BYD" / "BYD_DOLPHIN_2025.pdf"
    manual.parent.mkdir()
    manual.touch()

    loaded = load_manuals(str(tmp_path))

    assert loaded == [
        {
            "make": "BYD",
            "model": "DOLPHIN",
            "year": "2025",
            "file_path": str(manual),
            "total_pages": None,
            "ocr_page_count": 0,
            "extraction_errors": [],
            "language": "en",
            "is_translated": False,
            "translated_path": None,
        }
    ]
