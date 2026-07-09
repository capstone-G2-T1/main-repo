"""
manual_loader.py

Scans data/raw_manuals/ for vehicle manual PDFs and extracts basic
metadata (make, model, year) for every manual found. Every valid PDF
under a make subfolder is loaded — there is no filename-based
reject/skip list, because the real repo's naming isn't strict enough
for that (year is often missing, and there's no language token).

Real folder structure (one subfolder per make):

    data/raw_manuals/
    ├── BYD/
    │   ├── BYD_DOLPHIN_2025.pdf
    │   ├── BYD_SEAGULL.pdf              <- no year
    │   └── BYD_SONG_PLUS_DM_I.pdf       <- no year
    ├── GAC/
    │   └── GAC_GS4.pdf                  <- no year
    ├── HAVAL/
    │   └── HAVAL_H1_2017.pdf            <- has year
    └── ...

Metadata extraction rules:
- MAKE  -> the subfolder name the PDF lives in (e.g. "BYD"). This is
           more reliable than trying to parse it out of the filename,
           since every file is already organized that way.
- MODEL -> the filename, with the make prefix stripped (if repeated
           there) and the year stripped (if present), remaining
           underscores turned into spaces.
- YEAR  -> a 4-digit token anywhere in the filename. None if no such
           token exists — this is common and NOT treated as invalid.

Language is intentionally NOT extracted here. None of the manuals in
the real repo carry a language token in their filename, and per the
project's corpus-language decision, source language gets handled by
the translation step during ingestion, not the loader.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("manual_loader")


@dataclass
class ManualMetadata:
    """Structured metadata returned for every manual found."""
    make: str
    model: str
    year: Optional[str]
    file_path: str


def _parse_manual(pdf_path: Path, make_folder: str) -> ManualMetadata:
    """
    Build ManualMetadata for a single PDF.

    `make_folder` is the name of the immediate parent directory
    (e.g. "BYD", "GAC") and is trusted as the make, since the repo
    is already organized that way.

    Filenames are NOT consistently delimited in the real repo — some
    use underscores ("BYD_SONG_PLUS_DM_I.pdf"), others use spaces and
    hyphens ("BYD dolphin-2025.pdf"). Python's regex \b (word boundary)
    treats "_" as a word character, so "_2025" or "BYD_SONG" would
    never match \b2025\b or \bBYD\b — there's no boundary between two
    word characters. To sidestep this entirely, delimiters are
    normalized to spaces FIRST, before any \b-based matching:
      1. Normalize underscores/hyphens -> spaces.
      2. Pull the year out with a word-boundary regex search.
      3. Strip the make name out (case-insensitive, whole word).
    """
    stem = pdf_path.stem  # filename without ".pdf"

    # 1. Normalize delimiters to spaces FIRST so every \b check below
    #    behaves the same regardless of the original filename style.
    remainder = re.sub(r"[_\-]+", " ", stem)

    # 2. Extract year (search, not split — works regardless of position)
    year: Optional[str] = None
    year_match = re.search(r"\b(19|20)\d{2}\b", remainder)
    if year_match:
        year = year_match.group(0)
        remainder = remainder[:year_match.start()] + remainder[year_match.end():]

    # 3. Strip the make name if it's repeated in the filename
    #    (case-insensitive, word boundary so "GS4" doesn't get mangled by "S4")
    remainder = re.sub(
        rf"\b{re.escape(make_folder)}\b", "", remainder, flags=re.IGNORECASE
    )

    remainder = re.sub(r"\s+", " ", remainder).strip()

    model = remainder if remainder else stem

    return ManualMetadata(
        make=make_folder,
        model=model,
        year=year,
        file_path=str(pdf_path),
    )


def load_manuals(raw_manuals_dir: str = "data/raw_manuals") -> List[dict]:
    """
    Scan `raw_manuals_dir` recursively (one level of make subfolders)
    and return structured metadata for every PDF found.

    Every PDF under a make subfolder is loaded — nothing is skipped
    for missing year, since that's common in the real data. A PDF
    sitting directly in raw_manuals_dir with no make subfolder is
    logged as invalid and skipped, since we have no way to know its
    make in that case.
    """
    directory = Path(raw_manuals_dir)

    if not directory.exists():
        logger.error("Raw manuals directory does not exist: %s", directory)
        return []

    results: List[dict] = []
    skipped = 0

    # Anything directly inside raw_manuals_dir (not in a make subfolder)
    # can't be attributed a make reliably -> skip and log.
    for loose_pdf in directory.glob("*.pdf"):
        logger.warning(
            "Skipping PDF with no make subfolder (expected data/raw_manuals/<MAKE>/%s): %s",
            loose_pdf.name, loose_pdf.name,
        )
        skipped += 1

    # Walk each make subfolder (e.g. BYD/, GAC/, GEELY/, HAVAL/, MG/, ORA/, VW/)
    make_folders = sorted(p for p in directory.iterdir() if p.is_dir())

    if not make_folders:
        logger.warning("No make subfolders found in %s", directory)

    for make_dir in make_folders:
        make_name = make_dir.name
        pdf_files = sorted(make_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning("No PDFs found for make folder: %s", make_name)
            continue

        for pdf_path in pdf_files:
            metadata = _parse_manual(pdf_path, make_name)
            logger.info(
                "Loaded manual: make=%s model=%s year=%s file=%s",
                metadata.make, metadata.model, metadata.year or "unknown",
                pdf_path.name,
            )
            results.append(asdict(metadata))

    logger.info(
        "Manual loading complete: %d loaded, %d skipped (no make folder)",
        len(results), skipped,
    )

    return results


if __name__ == "__main__":
    # Quick manual test run: python manual_loader.py
    manuals = load_manuals()
    for m in manuals:
        print(m)
