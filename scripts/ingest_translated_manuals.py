from __future__ import annotations

import argparse
import hashlib
import html
import importlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for path in (ROOT, BACKEND):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


INPUT_DIR = ROOT / "data" / "translated_manuals"
METADATA_FILENAME = "manuals_metadata.json"
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_BATCH_SIZE = 32
DEFAULT_COLLECTION = "vehicle_manual_chunks"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

LOGGER = logging.getLogger("translated_manual_ingestion")

ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
IMAGE_MARKER = re.compile(r"(?:الصورة|صورة|Ø§Ù„ØµÙˆØ±Ø©|ØµÙˆØ±Ø©)\s*\[\[[^\]]+\]\]")
PAGE_NUMBER_ONLY = re.compile(r"^\s*(?:\d+|[IVXLCDM]+)\s*$", re.IGNORECASE)
HTML_PRESENTATION_TAGS = re.compile(r"</?(?:center|font|span|div|p|br)\b[^>]*>", re.IGNORECASE)
HTML_TAG = re.compile(r"<[^>]+>")
INVALID_JSON_ESCAPE = re.compile(r'\\(?!["\\/bfnrtu])')
MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?؟؛。])\s+")
WARNING_HEADINGS = {
    "تحذير",
    "تنبيه",
    "انتباه",
    "تذكير",
    "ØªØ­Ø°ÙŠØ±",
    "ØªÙ†Ø¨ÙŠÙ‡",
    "Ø§Ù†ØªØ¨Ø§Ù‡",
    "ØªØ°ÙƒÙŠØ±",
}


@dataclass
class Page:
    page_number: int
    text: str


@dataclass
class ManualMetadata:
    manual_name: str
    make: str | None
    model: str | None
    trim: str | None
    year: int | None
    language: str
    source_file: str


@dataclass
class Chunk:
    chunk_id: str
    manual_name: str
    make: str | None
    model: str | None
    trim: str | None
    year: int | None
    language: str
    page_number: int
    chunk_index: int
    section_title: str | None
    source_file: str
    text: str
    text_hash: str


@dataclass
class PreparedManual:
    path: Path
    metadata: ManualMetadata
    pages: list[Page]
    chunks: list[Chunk]
    content_hash: str
    pages_read: int
    empty_skipped: int
    invalid_skipped: int
    meaningless_skipped: int
    warnings: list[str] = field(default_factory=list)


@dataclass
class Summary:
    discovered: int = 0
    completed: int = 0
    skipped: int = 0
    failed: int = 0
    pages_read: int = 0
    empty_skipped: int = 0
    invalid_skipped: int = 0
    meaningless_skipped: int = 0
    chunks: int = 0
    embeddings: int = 0
    chroma: int = 0
    postgres: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest translated Arabic vehicle manual JSON files.")
    parser.add_argument("--manual", help="Process one JSON file from data/translated_manuals")
    parser.add_argument("--force", action="store_true", help="Replace existing manual chunks and vectors")
    parser.add_argument("--dry-run", action="store_true", help="Validate, normalize, and chunk without external writes")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--collection", help="Override the configured Chroma collection name")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if not 0 <= args.chunk_overlap < args.chunk_size:
        parser.error("--chunk-overlap must satisfy 0 <= overlap < chunk-size")
    return args


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_project_settings() -> Any | None:
    try:
        return importlib.import_module("core.config").settings
    except Exception:
        return None


def discover_manual_files(selected: str | None = None, input_dir: Path = INPUT_DIR) -> list[Path]:
    if selected:
        path = input_dir / selected
        return [path] if path.exists() and path.name != METADATA_FILENAME else []
    return sorted(path for path in input_dir.glob("*.json") if path.name != METADATA_FILENAME)


def load_optional_metadata(input_dir: Path = INPUT_DIR) -> dict[str, dict[str, Any]]:
    path = input_dir / METADATA_FILENAME
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        LOGGER.warning("Ignoring invalid metadata file %s: %s", path, exc)
        return {}
    if not isinstance(data, dict):
        LOGGER.warning("Ignoring %s because root value is not an object", path)
        return {}
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}


def is_meaningless_page(text: str) -> bool:
    stripped = text.strip()
    if not stripped or PAGE_NUMBER_ONLY.match(stripped):
        return True
    compact = re.sub(r"\s+", " ", stripped).strip().lower()
    meaningless = {
        "جدول المحتويات",
        "المحتويات",
        "www.manualslib.com",
        "manualslib",
        "مشاريع manualslib الأخرى",
    }
    return compact in meaningless


def normalize_arabic_text(text: str) -> str:
    text = html.unescape(text)
    text = CONTROL_CHARS.sub(" ", text)
    text = IMAGE_MARKER.sub(" ", text)
    text = re.sub(r"</?\s*td\b[^>]*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</?\s*th\b[^>]*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</?\s*tr\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?\s*table\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = HTML_PRESENTATION_TAGS.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = ARABIC_DIACRITICS.sub("", text)
    text = text.replace("\u0640", "")
    text = text.replace("•", "\n").replace("◦", "\n").replace("▪", "\n").replace("●", "\n")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_and_validate_pages(path: Path) -> tuple[list[Page], int, int, int, int, list[str]]:
    warnings: list[str] = []
    raw_text = path.read_text(encoding="utf-8")
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        repaired_text = INVALID_JSON_ESCAPE.sub(r"\\\\", raw_text)
        if repaired_text == raw_text:
            raise ValueError(f"invalid JSON: {exc}") from exc
        try:
            raw = json.loads(repaired_text)
            warnings.append(f"repaired invalid JSON escapes in {path.name}")
        except json.JSONDecodeError:
            raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError("JSON root must be a list")

    pages: list[Page] = []
    seen: set[int] = set()
    empty_skipped = invalid_skipped = meaningless_skipped = 0
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            invalid_skipped += 1
            warnings.append(f"item {index} is not an object")
            continue
        try:
            page_number = int(item.get("page_number"))
        except (TypeError, ValueError):
            invalid_skipped += 1
            warnings.append(f"item {index} has invalid page_number")
            continue
        if page_number <= 0:
            invalid_skipped += 1
            warnings.append(f"item {index} has non-positive page_number")
            continue
        text = item.get("text")
        if not isinstance(text, str):
            invalid_skipped += 1
            warnings.append(f"page {page_number} text is not a string")
            continue
        if page_number in seen:
            warnings.append(f"duplicate page_number {page_number}")
        seen.add(page_number)
        if not text.strip():
            empty_skipped += 1
            continue
        normalized = normalize_arabic_text(text)
        if is_meaningless_page(normalized):
            meaningless_skipped += 1
            continue
        pages.append(Page(page_number=page_number, text=normalized))

    pages.sort(key=lambda page: page.page_number)
    if not pages:
        raise ValueError("manual has no usable pages")
    return pages, len(raw), empty_skipped, invalid_skipped, meaningless_skipped, warnings


def parse_year(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        year = int(str(value).split("-")[0])
    except ValueError:
        return None
    return year if 1800 <= year <= 2200 else None


def metadata_from_filename(path: Path) -> ManualMetadata:
    stem = path.stem
    if stem.endswith(".ar"):
        stem = stem[:-3]
    parts = [part for part in re.split(r"[_\-\s]+", stem) if part]
    year = next((parse_year(part) for part in parts if parse_year(part)), None)
    non_year = [part for part in parts if parse_year(part) is None]
    make = non_year[0].title() if non_year else None
    model = " ".join(non_year[1:]) if len(non_year) > 1 else None
    return ManualMetadata(
        manual_name=stem,
        make=make,
        model=model,
        trim=None,
        year=year,
        language="ar",
        source_file=path.name,
    )


def extract_manual_metadata(path: Path, pages: list[Page], config: dict[str, dict[str, Any]]) -> ManualMetadata:
    base = metadata_from_filename(path)
    configured = config.get(path.name)
    if configured is None and path.name.endswith(".ar.json"):
        configured = config.get(path.name.replace(".ar.json", ".json"))
    if configured:
        return ManualMetadata(
            manual_name=str(configured.get("manual_name") or base.manual_name),
            make=configured.get("make", base.make),
            model=configured.get("model", base.model),
            trim=configured.get("trim", base.trim),
            year=parse_year(configured.get("year", base.year)),
            language=str(configured.get("language") or "ar"),
            source_file=path.name,
        )
    if (not base.make or not base.model) and pages:
        first_line = pages[0].text.splitlines()[0].strip() if pages[0].text.splitlines() else ""
        tokens = [token for token in re.split(r"\s+", first_line) if token and re.search(r"[A-Za-z]", token)]
        if not base.model and len(tokens) >= 2:
            base.model = tokens[-1]
    if not base.make or not base.model:
        LOGGER.warning("Metadata for %s is incomplete: make=%s model=%s", path.name, base.make, base.model)
    return base


def is_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if MARKDOWN_HEADING.match(stripped):
        return True
    if stripped in WARNING_HEADINGS:
        return True
    if len(stripped) <= 90 and not stripped.endswith((".", "،", ",", ";", "؛", "?", "؟", "!")):
        return True
    return False


def extract_section_title(text: str, fallback: str | None = None) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = MARKDOWN_HEADING.match(stripped)
        if match:
            return match.group(1).strip()[:255]
        if is_heading_line(stripped):
            return stripped[:255]
    return fallback


def split_units(text: str) -> list[str]:
    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        lines = paragraph.splitlines()
        if len(lines) == 1 and is_heading_line(lines[0]):
            units.append(lines[0].strip())
            continue
        buffer: list[str] = []
        for line in lines:
            if is_heading_line(line) and buffer:
                units.append("\n".join(buffer).strip())
                buffer = [line.strip()]
            else:
                buffer.append(line.strip())
        if buffer:
            block = "\n".join(buffer).strip()
            if len(block) <= 300:
                units.append(block)
            else:
                units.extend(part.strip() for part in SENTENCE_BOUNDARY.split(block) if part.strip())
    return units


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "manual"


def make_chunk_id(metadata: ManualMetadata, page_number: int, chunk_index: int, digest: str) -> str:
    return f"{stable_slug(metadata.manual_name)}_p{page_number}_c{chunk_index:03d}_{digest[:8]}"


def split_long_unit(unit: str, chunk_size: int, overlap: int) -> list[str]:
    if len(unit) <= chunk_size:
        return [unit]
    step = max(chunk_size - overlap, 1)
    chunks: list[str] = []
    start = 0
    while start < len(unit):
        end = min(start + chunk_size, len(unit))
        chunk = unit[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(unit):
            break
        start += step
    return chunks


def chunk_page(page: Page, metadata: ManualMetadata, start_index: int, chunk_size: int, overlap: int) -> list[Chunk]:
    units: list[str] = []
    for unit in split_units(page.text):
        units.extend(split_long_unit(unit, chunk_size, overlap))

    raw_chunks: list[str] = []
    current = ""
    for unit in units:
        candidate = unit if not current else f"{current}\n{unit}"
        if len(candidate) <= chunk_size or not current:
            current = candidate
            continue
        raw_chunks.append(current.strip())
        prefix = current[-overlap:].lstrip() if overlap else ""
        current = f"{prefix}\n{unit}".strip() if prefix else unit
    if current.strip():
        raw_chunks.append(current.strip())

    chunks: list[Chunk] = []
    section: str | None = None
    for offset, chunk_text in enumerate(raw_chunks):
        if len(chunk_text) < 40 and len(raw_chunks) > 1 and chunks:
            previous = chunks[-1]
            merged_text = f"{previous.text}\n{chunk_text}".strip()
            digest = text_hash(merged_text)
            chunks[-1] = Chunk(
                chunk_id=make_chunk_id(metadata, page.page_number, previous.chunk_index, digest),
                manual_name=previous.manual_name,
                make=previous.make,
                model=previous.model,
                trim=previous.trim,
                year=previous.year,
                language=previous.language,
                page_number=previous.page_number,
                chunk_index=previous.chunk_index,
                section_title=previous.section_title,
                source_file=previous.source_file,
                text=merged_text,
                text_hash=digest,
            )
            continue
        section = extract_section_title(chunk_text, section)
        digest = text_hash(chunk_text)
        chunk_index = start_index + len(chunks)
        chunks.append(
            Chunk(
                chunk_id=make_chunk_id(metadata, page.page_number, chunk_index, digest),
                manual_name=metadata.manual_name,
                make=metadata.make,
                model=metadata.model,
                trim=metadata.trim,
                year=metadata.year,
                language=metadata.language,
                page_number=page.page_number,
                chunk_index=chunk_index,
                section_title=section,
                source_file=metadata.source_file,
                text=chunk_text,
                text_hash=digest,
            )
        )
    return chunks


def build_chunks(pages: list[Page], metadata: ManualMetadata, chunk_size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in pages:
        chunks.extend(chunk_page(page, metadata, len(chunks), chunk_size, overlap))
    return chunks


def manual_content_hash(pages: list[Page]) -> str:
    payload = "\n".join(f"{page.page_number}:{page.text}" for page in pages)
    return text_hash(payload)


def prepare_manual(path: Path, metadata_config: dict[str, dict[str, Any]], chunk_size: int, overlap: int) -> PreparedManual:
    pages, pages_read, empty, invalid, meaningless, warnings = load_and_validate_pages(path)
    metadata = extract_manual_metadata(path, pages, metadata_config)
    chunks = build_chunks(pages, metadata, chunk_size, overlap)
    return PreparedManual(
        path=path,
        metadata=metadata,
        pages=pages,
        chunks=chunks,
        content_hash=manual_content_hash(pages),
        pages_read=pages_read,
        empty_skipped=empty,
        invalid_skipped=invalid,
        meaningless_skipped=meaningless,
        warnings=warnings,
    )


def configured_embedding_model() -> str:
    settings = get_project_settings()
    if settings is not None and getattr(settings, "EMBEDDING_MODEL", None):
        return str(settings.EMBEDDING_MODEL)
    return os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def load_embedding_model() -> tuple[Any, str]:
    model_name = configured_embedding_model()
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("sentence-transformers is required for real ingestion; use --dry-run to validate only") from exc
    LOGGER.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name), model_name


def generate_embeddings(texts: list[str], batch_size: int) -> tuple[list[list[float]], str, int]:
    if not texts:
        return [], configured_embedding_model(), 0
    model, model_name = load_embedding_model()
    vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
    embeddings = vectors.tolist() if hasattr(vectors, "tolist") else [list(vector) for vector in vectors]
    dimension = len(embeddings[0]) if embeddings else 0
    LOGGER.info("Generated %d embeddings with dimension %d using %s", len(embeddings), dimension, model_name)
    return embeddings, model_name, dimension


def configured_collection_name(override: str | None) -> str:
    if override:
        return override
    settings = get_project_settings()
    if settings is not None and getattr(settings, "CHROMA_COLLECTION_NAME", None):
        return str(settings.CHROMA_COLLECTION_NAME)
    return os.getenv("CHROMA_COLLECTION_NAME", DEFAULT_COLLECTION)


def create_chroma_client(collection_name: str) -> Any:
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("chromadb is required for real ingestion; use --dry-run to validate only") from exc

    persist_path = os.getenv("CHROMA_PERSIST_DIRECTORY") or os.getenv("CHROMA_DB_DIR")
    if persist_path:
        return chromadb.PersistentClient(path=persist_path).get_or_create_collection(name=collection_name)

    settings = get_project_settings()
    host = os.getenv("CHROMA_HOST", str(getattr(settings, "CHROMA_HOST", "chroma") if settings else "chroma"))
    port = int(os.getenv("CHROMA_PORT", str(getattr(settings, "CHROMA_PORT", 8000) if settings else 8000)))
    return chromadb.HttpClient(host=host, port=port).get_or_create_collection(name=collection_name)


def make_chroma_safe_metadata(chunk: Chunk) -> dict[str, str | int | float | bool]:
    raw = {
        "manual_name": chunk.manual_name,
        "make": chunk.make,
        "model": chunk.model,
        "trim": chunk.trim,
        "year": chunk.year,
        "language": chunk.language,
        "page_number": chunk.page_number,
        "chunk_index": chunk.chunk_index,
        "section_title": chunk.section_title,
        "source_file": chunk.source_file,
        "text_hash": chunk.text_hash,
    }
    return {key: value for key, value in raw.items() if value is not None and isinstance(value, (str, int, float, bool))}


def remove_stale_chroma_chunks(collection: Any, manual_name: str, chunk_ids: list[str] | None = None) -> None:
    try:
        collection.delete(where={"manual_name": manual_name})
        return
    except Exception as exc:
        LOGGER.warning("Chroma delete by manual_name failed for %s: %s", manual_name, exc)
    if chunk_ids:
        try:
            collection.delete(ids=chunk_ids)
        except Exception as exc:
            LOGGER.warning("Chroma delete by ids failed for %s: %s", manual_name, exc)


def upsert_chroma_chunks(collection: Any, chunks: list[Chunk], embeddings: list[list[float]]) -> int:
    if not chunks:
        return 0
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.text for chunk in chunks],
        metadatas=[make_chroma_safe_metadata(chunk) for chunk in chunks],
    )
    return len(chunks)


def database_url() -> str:
    settings = get_project_settings()
    if settings is not None and getattr(settings, "sqlalchemy_database_url", None):
        return str(settings.sqlalchemy_database_url)
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB")
    if not all([user, password, host, db_name]):
        raise RuntimeError("PostgreSQL configuration is missing; set DATABASE_URL or POSTGRES_* variables")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def create_postgres_engine() -> Any:
    try:
        from db.session import engine as existing_engine

        return existing_engine
    except Exception:
        pass
    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise RuntimeError("sqlalchemy is required for PostgreSQL ingestion") from exc
    return create_engine(database_url(), pool_pre_ping=True)


def inspect_existing_schema(connection: Any) -> dict[str, set[str]]:
    try:
        result = connection.execute(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name IN ('vehicles', 'manuals', 'manual_chunks')
            """
        )
    except Exception:
        from sqlalchemy import text as sql_text

        result = connection.execute(
            sql_text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name IN ('vehicles', 'manuals', 'manual_chunks')
                """
            )
        )
    schema: dict[str, set[str]] = {}
    for table_name, column_name in result:
        schema.setdefault(str(table_name), set()).add(str(column_name))
    if "manuals" not in schema or "manual_chunks" not in schema:
        raise RuntimeError("PostgreSQL schema has no usable manuals/manual_chunks tables")
    return schema


def execute(connection: Any, statement: str, params: dict[str, Any] | None = None) -> Any:
    try:
        from sqlalchemy import text as sql_text

        return connection.execute(sql_text(statement), params or {})
    except ImportError:
        return connection.execute(statement, params or {})


def select_one(connection: Any, statement: str, params: dict[str, Any] | None = None) -> Any | None:
    result = execute(connection, statement, params)
    return result.mappings().first()


def get_or_create_vehicle(connection: Any, schema: dict[str, set[str]], metadata: ManualMetadata) -> Any:
    vehicle_columns = schema.get("vehicles", set())
    if not {"id", "make", "model", "year"}.issubset(vehicle_columns):
        raise RuntimeError("vehicles table does not have required id/make/model/year columns")
    make = metadata.make or "Unknown"
    model = metadata.model or metadata.manual_name
    year = metadata.year if metadata.year is not None else 0
    trim_clause = "trim IS NOT DISTINCT FROM :trim" if "trim" in vehicle_columns else "1=1"
    row = select_one(
        connection,
        f"SELECT id FROM vehicles WHERE make = :make AND model = :model AND year = :year AND {trim_clause} LIMIT 1",
        {"make": make, "model": model, "year": year, "trim": metadata.trim},
    )
    if row:
        return row["id"]
    columns = ["make", "model", "year"]
    values: dict[str, Any] = {"make": make, "model": model, "year": year}
    if "trim" in vehicle_columns:
        columns.append("trim")
        values["trim"] = metadata.trim
    placeholders = ", ".join(f":{column}" for column in columns)
    row = select_one(
        connection,
        f"INSERT INTO vehicles ({', '.join(columns)}) VALUES ({placeholders}) RETURNING id",
        values,
    )
    return row["id"]


def existing_manual(connection: Any, schema: dict[str, set[str]], metadata: ManualMetadata, content_hash: str) -> Any | None:
    manual_columns = schema["manuals"]
    filters: list[str] = []
    params: dict[str, Any] = {
        "checksum": content_hash,
        "source_path": str(INPUT_DIR / metadata.source_file),
        "translated_path": str(INPUT_DIR / metadata.source_file),
        "manual_name": metadata.manual_name,
    }
    if "checksum" in manual_columns:
        filters.append("checksum = :checksum")
    if "source_path" in manual_columns:
        filters.append("source_path = :source_path")
    if "translated_path" in manual_columns:
        filters.append("translated_path = :translated_path")
    if "manual_name" in manual_columns:
        filters.append("manual_name = :manual_name")
    if not filters:
        return None
    return select_one(connection, f"SELECT * FROM manuals WHERE {' OR '.join(filters)} LIMIT 1", params)


def delete_manual_chunks(connection: Any, manual_id: Any) -> None:
    execute(connection, "DELETE FROM manual_chunks WHERE manual_id = :manual_id", {"manual_id": manual_id})


def delete_manual_record(connection: Any, manual_id: Any) -> None:
    execute(connection, "DELETE FROM manuals WHERE id = :manual_id", {"manual_id": manual_id})


def insert_manual_record(
    connection: Any,
    schema: dict[str, set[str]],
    metadata: ManualMetadata,
    path: Path,
    content_hash: str,
    total_pages: int,
    total_chunks: int,
) -> Any:
    vehicle_id = get_or_create_vehicle(connection, schema, metadata)
    supported = schema["manuals"]
    values: dict[str, Any] = {
        "vehicle_id": vehicle_id,
        "manual_name": metadata.manual_name,
        "language": metadata.language,
        "checksum": content_hash,
        "is_translated": True,
        "source_path": str(path),
        "translated_path": str(path),
        "total_pages": total_pages,
        "total_chunks": total_chunks,
        "content_hash": content_hash,
        "ingestion_status": "processing",
        "source_file": metadata.source_file,
    }
    columns = [column for column in values if column in supported]
    if "id" not in supported or not {"manual_name", "language"}.issubset(supported):
        raise RuntimeError("manuals table does not have required id/manual_name/language columns")
    placeholders = ", ".join(f":{column}" for column in columns)
    row = select_one(
        connection,
        f"INSERT INTO manuals ({', '.join(columns)}) VALUES ({placeholders}) RETURNING id",
        {column: values[column] for column in columns},
    )
    return row["id"]


def update_manual_status(connection: Any, schema: dict[str, set[str]], manual_id: Any, status: str) -> None:
    if "ingestion_status" not in schema["manuals"]:
        return
    execute(connection, "UPDATE manuals SET ingestion_status = :status WHERE id = :id", {"status": status, "id": manual_id})


def insert_chunk_records(connection: Any, schema: dict[str, set[str]], manual_id: Any, chunks: list[Chunk], collection_name: str) -> int:
    supported = schema["manual_chunks"]
    inserted = 0
    for chunk in chunks:
        values = {
            "manual_id": manual_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "section": chunk.section_title,
            "section_title": chunk.section_title,
            "chunk_text": chunk.text,
            "text": chunk.text,
            "text_hash": chunk.text_hash,
            "chroma_collection": collection_name,
            "chroma_vector_id": chunk.chunk_id,
            "chroma_id": chunk.chunk_id,
            "chunk_id": chunk.chunk_id,
        }
        columns = [column for column in values if column in supported]
        required = {"manual_id", "chunk_index", "page_number"}
        if not required.issubset(set(columns)):
            raise RuntimeError("manual_chunks table is missing required columns")
        placeholders = ", ".join(f":{column}" for column in columns)
        execute(
            connection,
            f"INSERT INTO manual_chunks ({', '.join(columns)}) VALUES ({placeholders})",
            {column: values[column] for column in columns},
        )
        inserted += 1
    return inserted


def save_to_postgres(prepared: PreparedManual, collection_name: str, force: bool) -> tuple[str, int]:
    engine = create_postgres_engine()
    with engine.begin() as connection:
        schema = inspect_existing_schema(connection)
        existing = existing_manual(connection, schema, prepared.metadata, prepared.content_hash)
        if existing and existing.get("checksum") == prepared.content_hash and not force:
            LOGGER.info("%s is already up to date; skipping PostgreSQL writes", prepared.metadata.source_file)
            return "skipped", 0
        if existing:
            delete_manual_chunks(connection, existing["id"])
            delete_manual_record(connection, existing["id"])
        manual_id = insert_manual_record(
            connection,
            schema,
            prepared.metadata,
            prepared.path,
            prepared.content_hash,
            len(prepared.pages),
            len(prepared.chunks),
        )
        try:
            saved = insert_chunk_records(connection, schema, manual_id, prepared.chunks, collection_name)
            update_manual_status(connection, schema, manual_id, "completed")
            return "completed", saved
        except Exception:
            update_manual_status(connection, schema, manual_id, "failed")
            raise


def postgres_manual_state(prepared: PreparedManual, force: bool) -> str:
    """Return new, replace, or up_to_date using only the existing schema."""
    engine = create_postgres_engine()
    with engine.begin() as connection:
        schema = inspect_existing_schema(connection)
        existing = existing_manual(connection, schema, prepared.metadata, prepared.content_hash)
        if not existing:
            return "new"
        if existing.get("checksum") == prepared.content_hash and not force:
            return "up_to_date"
        return "replace"


def process_manual(path: Path, metadata_config: dict[str, dict[str, Any]], args: argparse.Namespace) -> tuple[str, PreparedManual, int, int, int]:
    stage = "loading"
    prepared: PreparedManual | None = None
    collection = None
    try:
        stage = "validation"
        prepared = prepare_manual(path, metadata_config, args.chunk_size, args.chunk_overlap)
        for warning in prepared.warnings:
            LOGGER.warning("%s: %s", path.name, warning)
        LOGGER.info(
            "Prepared source_file=%s manual_name=%s pages=%d chunks=%d",
            prepared.metadata.source_file,
            prepared.metadata.manual_name,
            len(prepared.pages),
            len(prepared.chunks),
        )
        if args.dry_run:
            return "completed", prepared, 0, 0, 0

        stage = "postgres-precheck"
        manual_state = postgres_manual_state(prepared, args.force)
        if manual_state == "up_to_date":
            LOGGER.info("%s is already up to date; skipping embeddings and writes", prepared.metadata.source_file)
            return "skipped", prepared, 0, 0, 0

        stage = "embedding"
        embeddings, _model_name, _dimension = generate_embeddings([chunk.text for chunk in prepared.chunks], args.batch_size)
        collection_name = configured_collection_name(args.collection)
        stage = "chroma"
        collection = create_chroma_client(collection_name)
        existing_ids = [chunk.chunk_id for chunk in prepared.chunks]
        if args.force or manual_state == "replace":
            remove_stale_chroma_chunks(collection, prepared.metadata.manual_name, existing_ids)
        chroma_count = upsert_chroma_chunks(collection, prepared.chunks, embeddings)
        stage = "postgres"
        status, postgres_count = save_to_postgres(prepared, collection_name, args.force)
        if status == "skipped":
            remove_stale_chroma_chunks(collection, prepared.metadata.manual_name, existing_ids)
            return "skipped", prepared, len(embeddings), 0, 0
        return "completed", prepared, len(embeddings), chroma_count, postgres_count
    except Exception as exc:
        if collection is not None and prepared is not None:
            remove_stale_chroma_chunks(collection, prepared.metadata.manual_name, [chunk.chunk_id for chunk in prepared.chunks])
        LOGGER.error("%s failed at stage=%s: %s", path.name, stage, exc)
        raise


def print_summary(summary: Summary, dry_run: bool) -> None:
    print("=" * 50)
    print("Translated Manuals Ingestion Summary")
    print("=" * 50)
    print(f"Manuals discovered:          {summary.discovered}")
    print(f"Manuals completed:           {summary.completed}")
    print(f"Manuals skipped:             {summary.skipped}")
    print(f"Manuals failed:              {summary.failed}")
    print(f"Pages read:                  {summary.pages_read}")
    print(f"Empty pages skipped:         {summary.empty_skipped}")
    print(f"Invalid pages skipped:       {summary.invalid_skipped}")
    print(f"Meaningless pages skipped:   {summary.meaningless_skipped}")
    print(f"Chunks generated:            {summary.chunks}")
    print(f"Embeddings generated:        {summary.embeddings}")
    print(f"Chroma records upserted:     {summary.chroma}")
    print(f"PostgreSQL records saved:    {summary.postgres}")
    if dry_run:
        print("DRY RUN: no embeddings generated and no data written to Chroma or PostgreSQL.")
    print("=" * 50)


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    metadata_config = load_optional_metadata()
    manual_files = discover_manual_files(args.manual)
    summary = Summary(discovered=len(manual_files))
    if args.manual and not manual_files:
        LOGGER.error("Manual not found in %s: %s", INPUT_DIR, args.manual)
        print_summary(summary, args.dry_run)
        return 1

    for path in manual_files:
        try:
            status, prepared, embeddings, chroma_count, postgres_count = process_manual(path, metadata_config, args)
            summary.pages_read += prepared.pages_read
            summary.empty_skipped += prepared.empty_skipped
            summary.invalid_skipped += prepared.invalid_skipped
            summary.meaningless_skipped += prepared.meaningless_skipped
            summary.chunks += len(prepared.chunks)
            summary.embeddings += embeddings
            summary.chroma += chroma_count
            summary.postgres += postgres_count
            if status == "skipped":
                summary.skipped += 1
            else:
                summary.completed += 1
        except Exception:
            summary.failed += 1
            continue

    print_summary(summary, args.dry_run)
    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
