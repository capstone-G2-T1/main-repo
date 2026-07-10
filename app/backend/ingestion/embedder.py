"""
app/backend/ingestion/embedder.py

Generates multilingual sentence embeddings for manual chunks using
paraphrase-multilingual-MiniLM-L12-v2 -- the same embedding model listed
as the primary embedding in the README/config, so chunk vectors and
query vectors live in the same space at retrieval time.

The model is loaded lazily and cached, since constructing it is the
expensive part; embedding calls themselves just run inference on an
already-loaded model.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger("embedder")

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of chunk texts.

    Returns one vector (as a plain list of floats, ready for Chroma) per
    input text, in the same order as `texts`. An empty input list returns
    an empty output list without loading the model.
    """
    if not texts:
        return []

    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()
