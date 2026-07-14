"""Automated evaluation for the vehicle-manual RAG system.

The script loads a JSON evaluation set, runs questions through the backend RAG
pipeline, computes retrieval/answer metrics, and writes:

* eval_results.csv
* eval_summary.json

It can also compare the requested RAG variants and generate a report table:

    python scripts/run_eval.py --dataset test_questions.json --all-variants
"""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import logging
import os
import sys
import time
from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterator
from unittest.mock import patch


os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY", "False")
os.environ.setdefault("CHROMA_HOST", "localhost")
os.environ.setdefault("CHROMA_PORT", "8001")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "app" / "backend"
for import_path in (ROOT, BACKEND):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))


LOGGER = logging.getLogger("run_eval")
LATENCY_SLA_MS = 30_000
DEFAULT_VARIANTS = (
    "baseline_vector_rag",
    "rag_normalization",
    "rag_ner_filtering",
    "rag_reranker",
    "full_system",
)
VARIANT_LABELS = {
    "baseline_vector_rag": "Baseline vector RAG",
    "rag_normalization": "Vector RAG + normalization",
    "rag_ner_filtering": "Vector RAG + NER filtering",
    "rag_reranker": "Vector RAG + reranker",
    "full_system": "Full system",
}
REJECTION_PHRASES = (
    "لم أجد",
    "لا توجد معلومات",
    "غير كافية",
    "غير موجود",
    "not found",
    "insufficient",
)


@dataclass
class TestQuestion:
    id: str | int | None
    question: str
    manual: str | None = None
    make: str | None = None
    model: str | None = None
    expected_page: int | None = None
    expected_section: str | None = None
    expected_answer_substring: str | None = None
    intent: str | None = None
    system: str | None = None
    should_refuse: bool = False


@dataclass
class QuestionResult:
    variant: str
    id: str | int | None
    question: str
    expected_manual: str | None
    make: str | None
    model: str | None
    expected_page: int | None
    expected_section: str | None
    expected_answer_substring: str | None
    expected_intent: str | None
    should_refuse: bool
    pipeline_answer: str
    pipeline_intent: str | None
    citation_pages: list[int]
    retrieval_pages: list[int]
    citation_manuals: list[str]
    predicted_manual_pages: list[str]
    retrieved_chunk_count: int
    refused: bool
    scope: str | None
    normalized_question: str | None
    metadata_filter: dict[str, Any] | None
    latency_ms: float
    pipeline_error: str | None
    recall_at_3: bool | None = None
    recall_at_5: bool | None = None
    mrr: float | None = None
    citation_accuracy: bool | None = None
    rejection_accuracy: bool | None = None
    answer_substring_match: bool | None = None
    within_sla: bool = False


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load_dataset(path: Path) -> list[TestQuestion]:
    """Load test_questions.json into normalized TestQuestion objects."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Dataset must be a JSON array")

    questions: list[TestQuestion] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict) or not item.get("question"):
            LOGGER.warning("Skipping invalid dataset item at index %d", index)
            continue
        questions.append(
            TestQuestion(
                id=item.get("id", index),
                question=str(item["question"]),
                manual=item.get("manual") or item.get("expected_manual"),
                make=item.get("make"),
                model=item.get("model"),
                expected_page=_int_or_none(item.get("expected_page")),
                expected_section=item.get("expected_section"),
                expected_answer_substring=item.get("expected_answer_substring"),
                intent=item.get("intent"),
                system=item.get("system"),
                should_refuse=bool(item.get("should_refuse", item.get("expected_refusal", False))),
            )
        )
    return questions


def _selected_vehicle(question: TestQuestion) -> str | None:
    if question.make or question.model:
        return " ".join(part for part in (question.make, question.model) if part).strip()
    return None


@contextmanager
def _variant_patches(variant: str, retrieval_only: bool = False) -> Iterator[None]:
    """Patch pipeline stages to approximate each report variant."""
    pipeline = importlib.import_module("rag.pipeline")
    generator = importlib.import_module("rag.generator")
    types = importlib.import_module("rag.types")

    empty_entities = types.ExtractedEntities()

    def retrieval_only_answer(*args: Any) -> tuple[str, list[dict[str, Any]]]:
        chunks = args[-1]
        citations = generator._valid_citations(chunks)
        if not citations:
            return generator.NO_CONTEXT_REFUSAL, []
        return "Retrieval-only evaluation run; answer generation was skipped.", citations

    with ExitStack() as stack:
        if retrieval_only:
            stack.enter_context(patch.object(pipeline, "generate_answer", retrieval_only_answer))
        if variant == "baseline_vector_rag":
            stack.enter_context(patch.object(pipeline, "normalize_query", lambda question: question))
            stack.enter_context(patch.object(pipeline, "extract_entities", lambda _question: empty_entities))
            stack.enter_context(patch.object(pipeline, "build_metadata_filter", lambda *_args: {}))
            stack.enter_context(patch.object(pipeline, "rerank_chunks", lambda _query, chunks, top_k=None: chunks[: top_k or 5]))
        elif variant == "rag_normalization":
            stack.enter_context(patch.object(pipeline, "extract_entities", lambda _question: empty_entities))
            stack.enter_context(patch.object(pipeline, "build_metadata_filter", lambda *_args: {}))
            stack.enter_context(patch.object(pipeline, "rerank_chunks", lambda _query, chunks, top_k=None: chunks[: top_k or 5]))
        elif variant == "rag_ner_filtering":
            stack.enter_context(patch.object(pipeline, "rerank_chunks", lambda _query, chunks, top_k=None: chunks[: top_k or 5]))
        elif variant == "rag_reranker":
            stack.enter_context(patch.object(pipeline, "extract_entities", lambda _question: empty_entities))
            stack.enter_context(patch.object(pipeline, "build_metadata_filter", lambda *_args: {}))
        elif variant == "full_system":
            pass
        else:
            raise ValueError(f"Unknown variant: {variant}")
        yield


def call_pipeline(question: TestQuestion, variant: str, retrieval_only: bool = False) -> tuple[Any, float, str | None]:
    """Run the RAG pipeline in process and return result, latency, and error."""
    try:
        run_rag_pipeline = importlib.import_module("rag.pipeline").run_rag_pipeline
    except ImportError as exc:
        return None, 0.0, f"Import error: {exc}"

    start = time.perf_counter()
    try:
        with _variant_patches(variant, retrieval_only=retrieval_only):
            result = run_rag_pipeline(question.question, selected_vehicle=_selected_vehicle(question))
    except Exception as exc:  # external services and model calls can fail
        return None, (time.perf_counter() - start) * 1000, str(exc)
    return result, (time.perf_counter() - start) * 1000, None


def _extract_page(metadata: dict[str, Any]) -> int | None:
    from rag.metadata import canonicalize_metadata

    return _int_or_none(canonicalize_metadata(metadata).get("page"))


def _canonical_manual(value: Any) -> str | None:
    from rag.metadata import canonical_manual_name

    return canonical_manual_name(value)


def _citation_pages(citations: list[dict[str, Any]]) -> list[int]:
    pages: list[int] = []
    for citation in citations:
        page = _int_or_none(citation.get("page"))
        if page is not None:
            pages.append(page)
    return pages


def _retrieval_pages(result: Any) -> list[int]:
    chunks = _retrieved_chunks(result)
    pages: list[int] = []
    seen: set[int] = set()
    for chunk in chunks:
        metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}
        page = _extract_page(metadata) if isinstance(metadata, dict) else None
        if page is not None and page not in seen:
            seen.add(page)
            pages.append(page)
    return pages


def _retrieved_chunks(result: Any) -> list[dict[str, Any]]:
    chunks = getattr(result, "reranked_chunks", None) or getattr(result, "retrieved_chunks", None) or []
    return [chunk for chunk in chunks if isinstance(chunk, dict)]


def _manual_page_pairs(result: Any) -> list[tuple[str | None, int | None]]:
    from rag.metadata import canonicalize_metadata

    pairs: list[tuple[str | None, int | None]] = []
    for chunk in _retrieved_chunks(result):
        metadata = canonicalize_metadata(chunk.get("metadata", {}))
        pairs.append((_canonical_manual(metadata.get("manual_name")), _int_or_none(metadata.get("page"))))
    return pairs


def _first_rank(pairs: list[tuple[str | None, int | None]], expected_manual: str | None, expected_page: int, tolerance: int) -> int | None:
    expected = _canonical_manual(expected_manual)
    for rank, (manual, page) in enumerate(pairs, start=1):
        if page is None:
            continue
        manual_ok = expected is None or manual == expected
        if manual_ok and abs(page - expected_page) <= tolerance:
            return rank
    return None


def _looks_like_rejection(result: Any, answer: str, citations: list[dict[str, Any]]) -> bool:
    refused = bool(getattr(result, "refused", False))
    scope = getattr(result, "scope", None)
    insufficient = bool(getattr(result, "insufficient_evidence", False))
    if refused or scope == "out_of_scope":
        return not citations
    if insufficient:
        return False
    lowered = answer.casefold()
    return not answer.strip() or any(phrase.casefold() in lowered for phrase in REJECTION_PHRASES)


def score_question(
    question: TestQuestion,
    result: Any,
    latency_ms: float,
    error: str | None,
    tolerance: int,
    variant: str,
) -> QuestionResult:
    if result is None:
        return QuestionResult(
            variant=variant,
            id=question.id,
            question=question.question,
            expected_manual=_canonical_manual(question.manual),
            make=question.make,
            model=question.model,
            expected_page=question.expected_page,
            expected_section=question.expected_section,
            expected_answer_substring=question.expected_answer_substring,
            expected_intent=question.intent,
            should_refuse=question.should_refuse,
            pipeline_answer="",
            pipeline_intent=None,
            citation_pages=[],
            retrieval_pages=[],
            citation_manuals=[],
            predicted_manual_pages=[],
            retrieved_chunk_count=0,
            refused=False,
            scope=None,
            normalized_question=None,
            metadata_filter=None,
            latency_ms=latency_ms,
            pipeline_error=error,
        )

    answer = getattr(result, "answer", "") or ""
    citations = getattr(result, "citations", []) or []
    if not isinstance(citations, list):
        citations = []
    citation_pages = _citation_pages([c for c in citations if isinstance(c, dict)])
    retrieval_pages = _retrieval_pages(result)
    citation_manuals = [
        _canonical_manual(c.get("manual_name")) or ""
        for c in citations
        if isinstance(c, dict) and c.get("manual_name")
    ]
    manual_page_pairs = _manual_page_pairs(result)
    predicted_manual_pages = [f"{manual or ''}:{page or ''}" for manual, page in manual_page_pairs]
    refused = bool(getattr(result, "refused", False))
    scope = getattr(result, "scope", None)
    scored = QuestionResult(
        variant=variant,
        id=question.id,
        question=question.question,
        expected_manual=_canonical_manual(question.manual),
        make=question.make,
        model=question.model,
        expected_page=question.expected_page,
        expected_section=question.expected_section,
        expected_answer_substring=question.expected_answer_substring,
        expected_intent=question.intent,
        should_refuse=question.should_refuse,
        pipeline_answer=answer,
        pipeline_intent=getattr(result, "intent", None),
        citation_pages=citation_pages,
        retrieval_pages=retrieval_pages,
        citation_manuals=citation_manuals,
        predicted_manual_pages=predicted_manual_pages,
        retrieved_chunk_count=len(manual_page_pairs),
        refused=refused,
        scope=scope,
        normalized_question=getattr(result, "normalized_query", None),
        metadata_filter=getattr(result, "metadata_filter", None),
        latency_ms=latency_ms,
        pipeline_error=error,
        within_sla=latency_ms <= LATENCY_SLA_MS,
    )

    if question.should_refuse:
        scored.rejection_accuracy = _looks_like_rejection(result, answer, citations)
        return scored

    if question.expected_page is not None:
        rank = _first_rank(manual_page_pairs, question.manual, question.expected_page, tolerance)
        scored.recall_at_3 = rank is not None and rank <= 3
        scored.recall_at_5 = rank is not None and rank <= 5
        scored.mrr = 1.0 / rank if rank else 0.0
        first_citation = citations[0] if citations else None
        first_manual = _canonical_manual(first_citation.get("manual_name")) if isinstance(first_citation, dict) else None
        first_page = _int_or_none(first_citation.get("page")) if isinstance(first_citation, dict) else None
        expected_manual = _canonical_manual(question.manual)
        scored.citation_accuracy = (
            first_page is not None
            and (expected_manual is None or first_manual == expected_manual)
            and abs(first_page - question.expected_page) <= tolerance
        )

    if question.expected_answer_substring:
        scored.answer_substring_match = question.expected_answer_substring in answer

    return scored


CSV_FIELDS = [
    "variant",
    "id",
    "question",
    "expected_manual",
    "make",
    "model",
    "expected_page",
    "expected_section",
    "expected_answer_substring",
    "expected_intent",
    "should_refuse",
    "pipeline_answer",
    "pipeline_intent",
    "citation_pages",
    "retrieval_pages",
    "citation_manuals",
    "predicted_manual_pages",
    "retrieved_chunk_count",
    "refused",
    "scope",
    "normalized_question",
    "metadata_filter",
    "latency_ms",
    "pipeline_error",
    "recall_at_3",
    "recall_at_5",
    "mrr",
    "citation_accuracy",
    "rejection_accuracy",
    "answer_substring_match",
    "within_sla",
]


def _csv_row(result: QuestionResult) -> dict[str, Any]:
    row = asdict(result)
    row["citation_pages"] = "|".join(str(page) for page in result.citation_pages)
    row["retrieval_pages"] = "|".join(str(page) for page in result.retrieval_pages)
    row["citation_manuals"] = "|".join(result.citation_manuals)
    row["predicted_manual_pages"] = "|".join(result.predicted_manual_pages)
    row["metadata_filter"] = json.dumps(result.metadata_filter, ensure_ascii=False) if result.metadata_filter else ""
    row["latency_ms"] = round(result.latency_ms, 2)
    return row


def save_results(results: list[QuestionResult], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "eval_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(_csv_row(result) for result in results)


def _mean(values: list[float | bool | None]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    return round(mean(numeric), 4) if numeric else None


def build_summary(
    results: list[QuestionResult],
    dataset: Path,
    out_dir: Path,
    variant: str,
    tolerance: int,
    retrieval_only: bool = False,
    cold_start_latency_ms: float | None = None,
) -> dict[str, Any]:
    retrieval = [r for r in results if not r.should_refuse and r.expected_page is not None]
    refusals = [r for r in results if r.should_refuse]
    answer_quality = [r for r in results if not r.should_refuse and r.answer_substring_match is not None]
    return {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "system_variant": variant,
        "system_variant_label": VARIANT_LABELS.get(variant, variant),
        "dataset": str(dataset),
        "output_directory": str(out_dir),
        "page_tolerance": tolerance,
        "retrieval_only": retrieval_only,
        "total_questions": len(results),
        "retrieval_questions": len(retrieval),
        "refusal_questions": len(refusals),
        "successful_requests": sum(1 for r in results if not r.pipeline_error),
        "failed_requests": sum(1 for r in results if r.pipeline_error),
        "pipeline_errors": sum(1 for r in results if r.pipeline_error),
        "avg_returned_chunks": round(mean(r.retrieved_chunk_count for r in results), 2) if results else None,
        "recall_at_3": _mean([r.recall_at_3 for r in retrieval]),
        "recall_at_5": _mean([r.recall_at_5 for r in retrieval]),
        "mrr": _mean([r.mrr for r in retrieval]),
        "citation_accuracy": _mean([r.citation_accuracy for r in retrieval]),
        "rejection_accuracy": _mean([r.rejection_accuracy for r in refusals]),
        "answer_substring_match_rate": _mean([r.answer_substring_match for r in answer_quality]),
        "avg_warm_latency_ms": round(mean(r.latency_ms for r in results), 2) if results else None,
        "cold_start_latency_ms": round(cold_start_latency_ms, 2) if cold_start_latency_ms is not None else None,
        "avg_latency_ms": round(mean(r.latency_ms for r in results), 2) if results else None,
        "max_latency_ms": round(max(r.latency_ms for r in results), 2) if results else None,
        "within_sla_rate": _mean([r.within_sla for r in results]),
        "sla_threshold_ms": LATENCY_SLA_MS,
    }


def save_summary(summary: dict[str, Any], out_dir: Path) -> None:
    (out_dir / "eval_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_variant(
    questions: list[TestQuestion],
    dataset: Path,
    out_dir: Path,
    variant: str,
    tolerance: int,
    retrieval_only: bool = False,
) -> dict[str, Any]:
    LOGGER.info("Running variant: %s", variant)
    results: list[QuestionResult] = []
    cold_start_latency_ms = None
    if questions:
        _warm_result, cold_start_latency_ms, _warm_error = call_pipeline(
            questions[0],
            variant,
            retrieval_only=retrieval_only,
        )
    for index, question in enumerate(questions, start=1):
        result, latency_ms, error = call_pipeline(question, variant, retrieval_only=retrieval_only)
        scored = score_question(question, result, latency_ms, error, tolerance, variant)
        results.append(scored)
        LOGGER.info(
            "[%s %d/%d] recall@3=%s reject=%s latency=%.0fms",
            variant,
            index,
            len(questions),
            scored.recall_at_3,
            scored.rejection_accuracy,
            scored.latency_ms,
        )

    save_results(results, out_dir)
    summary = build_summary(results, dataset, out_dir, variant, tolerance, retrieval_only=retrieval_only, cold_start_latency_ms=cold_start_latency_ms)
    save_summary(summary, out_dir)
    return summary


def _fmt_metric(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def save_comparison(summaries: list[dict[str, Any]], out_dir: Path) -> None:
    fields = [
        "system_variant",
        "system_variant_label",
        "recall_at_3",
        "recall_at_5",
        "mrr",
        "citation_accuracy",
        "rejection_accuracy",
        "avg_latency_ms",
        "pipeline_errors",
        "avg_returned_chunks",
        "cold_start_latency_ms",
    ]
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "variant_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: summary.get(field) for field in fields} for summary in summaries)

    headers = ["Variant", "Recall@3", "Recall@5", "MRR", "Citation Acc.", "Rejection Acc.", "Avg Latency"]
    rows = [
        [
            summary["system_variant_label"],
            _fmt_metric(summary["recall_at_3"]),
            _fmt_metric(summary["recall_at_5"]),
            _fmt_metric(summary["mrr"]),
            _fmt_metric(summary["citation_accuracy"]),
            _fmt_metric(summary["rejection_accuracy"]),
            _fmt_metric(summary["avg_warm_latency_ms"]),
        ]
        for summary in summaries
    ]
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(row) + " |" for row in rows),
    ]
    best = max(summaries, key=lambda item: item.get("recall_at_3") or 0, default=None)
    analysis = (
        f"The strongest variant by Recall@3 is **{best['system_variant_label']}**. "
        "If the full system does not lead every metric, inspect the per-question CSV files; "
        "the usual causes are over-restrictive metadata filters, reranker model fallback, or unavailable generation service."
        if best
        else "No comparable summaries were produced."
    )
    report = "\n".join(
        [
            "# Evaluation",
            "",
            "## Variant Comparison",
            "",
            *table,
            "",
            "## Analysis",
            "",
            analysis,
            "",
            "Per-question outputs are saved under each variant directory.",
            "",
        ]
    )
    (out_dir / "EVALUATION.md").write_text(report, encoding="utf-8")


def print_summary(summary: dict[str, Any]) -> None:
    print(f"\n{summary['system_variant_label']}")
    print(f"Recall@3:          {_fmt_metric(summary['recall_at_3'])}")
    print(f"Recall@5:          {_fmt_metric(summary['recall_at_5'])}")
    print(f"MRR:               {_fmt_metric(summary['mrr'])}")
    print(f"Citation Accuracy: {_fmt_metric(summary['citation_accuracy'])}")
    print(f"Rejection Accuracy:{_fmt_metric(summary['rejection_accuracy'])}")
    print(f"Average Warm Latency: {_fmt_metric(summary['avg_warm_latency_ms'])} ms")
    print(f"Cold-start Latency:   {_fmt_metric(summary['cold_start_latency_ms'])} ms")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RAG evaluation metrics.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "eval" / "test_questions.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "eval" / "results")
    parser.add_argument("--variant", choices=DEFAULT_VARIANTS, default="full_system")
    parser.add_argument("--all-variants", action="store_true", help="Run all report variants and compare them.")
    parser.add_argument("--tolerance", type=int, default=0, help="Allowed page-number distance for page metrics.")
    parser.add_argument("--limit", type=int, help="Evaluate only the first N valid questions for quick debugging.")
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Skip Ollama answer generation and score retrieval/citation metrics only.",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.log_level)
    try:
        questions = load_dataset(args.dataset)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 1
    if not questions:
        LOGGER.error("Dataset contained no valid questions")
        return 1
    if args.limit is not None:
        if args.limit <= 0:
            LOGGER.error("--limit must be a positive integer")
            return 1
        questions = questions[: args.limit]

    if args.all_variants:
        summaries = [
            run_variant(
                questions,
                args.dataset,
                args.out_dir / variant,
                variant,
                args.tolerance,
                retrieval_only=args.retrieval_only,
            )
            for variant in DEFAULT_VARIANTS
        ]
        save_comparison(summaries, args.out_dir)
        for summary in summaries:
            print_summary(summary)
        LOGGER.info("Saved comparison table and EVALUATION.md to %s", args.out_dir)
        return 0

    summary = run_variant(
        questions,
        args.dataset,
        args.out_dir,
        args.variant,
        args.tolerance,
        retrieval_only=args.retrieval_only,
    )
    print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
