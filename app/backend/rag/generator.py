"""Grounded Arabic answer generation through the local Ollama service."""

from __future__ import annotations

import logging
import re
from typing import Any, Callable

import requests

from core.config import settings
from rag.metadata import canonicalize_metadata
from rag.types import ExtractedEntities, RetrievedChunk

logger = logging.getLogger("rag.generator")

NO_CONTEXT_REFUSAL = (
    "لم أجد معلومات كافية في دليل السيارة المحدد للإجابة عن هذا السؤال بدقة. "
    "يرجى إعادة صياغة السؤال أو التأكد من اختيار السيارة الصحيحة."
)


def _source(chunk: RetrievedChunk) -> dict[str, Any] | None:
    metadata = canonicalize_metadata(chunk.metadata)
    manual = metadata.get("manual_name")
    page = metadata.get("page")
    if not manual or page is None:
        return None
    try:
        page_number = int(page)
    except (TypeError, ValueError):
        return None
    section = metadata.get("section")
    return {"manual_name": str(manual), "page": page_number, "section": section or None}


def _valid_citations(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for chunk in chunks:
        citation = _source(chunk)
        if citation and (citation["manual_name"], citation["page"]) not in seen:
            seen.add((citation["manual_name"], citation["page"]))
            citations.append(citation)
    return citations


def _build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        source = _source(chunk)
        if not source or not chunk.text.strip():
            continue
        blocks.append(
            f"[Source {index}]\nManual: {source['manual_name']}\nPage: {source['page']}\n"
            f"Section: {source['section'] or 'غير محدد'}\nText: {chunk.text.strip()}"
        )
    return "\n\n".join(blocks)


def _strip_model_citations(answer: str) -> str:
    # Citations are rebuilt from trusted metadata so the model cannot invent pages.
    lines = [
        line
        for line in answer.splitlines()
        if not re.match(r"^\s*(?:المصدر|المراجع|source|citation)\s*:", line, re.IGNORECASE)
    ]
    return "\n".join(lines).strip()


def _post_json(url: str, payload: dict, timeout: float) -> dict:
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else {}


def generate_answer(
    original_question: str,
    normalized_question: str,
    entities: ExtractedEntities,
    intent: str,
    selected_vehicle: str | None,
    chunks: list[RetrievedChunk],
    *,
    post_json: Callable[[str, dict, float], dict] = _post_json,
) -> tuple[str, list[dict[str, Any]]]:
    """Generate only with cited context; otherwise return a deterministic refusal."""
    context = _build_context(chunks)
    citations = _valid_citations(chunks)
    if not context or not citations:
        return NO_CONTEXT_REFUSAL, []

    prompt = (
        "أنت مساعد متخصص في أدلة السيارات. أجب بالعربية فقط وباختصار. "
        "استخدم المعلومات الموجودة في السياق حصرا ولا تخمن. "
        "لا تكتب أرقام صفحات أو مصادر؛ سيضيف النظام المصادر الموثوقة لاحقا. "
        "إذا لم يكف السياق، قل بوضوح إن المعلومات غير كافية.\n\n"
        f"السيارة المختارة: {selected_vehicle or 'غير محددة'}\n"
        f"نوع السؤال: {intent}\nالسؤال: {original_question}\n"
        f"السؤال المنظم: {normalized_question}\n\n{context}"
    )
    payload = {"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        data = post_json(f"{settings.OLLAMA_HOST.rstrip('/')}/api/generate", payload, settings.OLLAMA_TIMEOUT_SECONDS)
        answer = data.get("response")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("empty Ollama response")
    except Exception as exc:  # local LLM service boundary
        logger.error("Ollama generation failed: %s", exc.__class__.__name__)
        return NO_CONTEXT_REFUSAL, []

    grounded_answer = _strip_model_citations(answer)
    if not grounded_answer:
        return NO_CONTEXT_REFUSAL, []
    sources = "، ".join(f"{item['manual_name']}، الصفحة {item['page']}" for item in citations)
    return f"{grounded_answer}\n\nالمصدر: {sources}.", citations
