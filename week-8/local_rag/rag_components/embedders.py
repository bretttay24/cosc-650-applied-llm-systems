"""Local and Azure AI Foundry embedding providers for the RAG application."""

# ===================== Imports =====================

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import mlflow
import numpy as np
from mlflow.entities import SpanType
from psycopg import sql


@dataclass
class Embedder:
    """A named embedding provider with its vector size and encoding function."""

    name: str
    dim: int
    encode: Callable


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """Normalize a batch of vectors to unit length.

    Args:
        vectors (np.ndarray): The input vectors to normalize.

    Returns:
        np.ndarray: The normalized `float32` vectors for cosine similarity.
    """
    vectors = np.asarray(vectors, dtype="float32")
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


# ============================================================================================================
#                                       Local Embeddings
# ============================================================================================================
""" This model runs on the local machine and stores its downloaded files in .hf_cache."""


minilm_model = None


def _minilm_encode(texts):
    """Load MiniLM on first use, then encode locally."""
    global minilm_model
    if minilm_model is None:
        os.environ["HF_HOME"] = str((Path(".") / ".hf_cache").resolve())
        from sentence_transformers import SentenceTransformer

        minilm_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    with mlflow.start_span(name="minilm_embedding", span_type=SpanType.EMBEDDING) as span:
        span.set_inputs({"text_count": len(texts), "model": "all-MiniLM-L6-v2"})
        vectors = minilm_model.encode(texts, normalize_embeddings=True, batch_size=64).astype("float32")
        span.set_outputs({"embedding_count": len(vectors), "embedding_dim": vectors.shape[1] if len(vectors) else 0})
        return vectors


minilm = Embedder(name="all-MiniLM-L6-v2", dim=384, encode=_minilm_encode)

# ============================================================================================================
#                                       Azure AI Foundry Embeddings
# ============================================================================================================

# On Foundry this is the deployment name, which need not match the model name.
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")


def _openai_encode(texts, model=EMBEDDING_DEPLOYMENT, dimensions=None, batch_size=256):
    """Encode a list of texts with Azure AI Foundry in batches.

    The API may return a batch out of order, so responses are sorted by their
    original index before the normalized vectors are returned.

    Args:
        texts: The texts to encode.
        model: The Azure OpenAI embedding deployment name.
        dimensions: Optional output vector size supported by the deployment.
        batch_size: The number of texts to send in each API request.

    Returns:
        np.ndarray: Normalized embeddings in the same order as `texts`.
    """
    from .clients import azure_openai_client

    with mlflow.start_span(name="foundry_embedding", span_type=SpanType.EMBEDDING) as span:
        span.set_inputs({"text_count": len(texts), "model": model, "batch_size": batch_size})
        vectors = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            kwargs = {"dimensions": dimensions} if dimensions else {}
            response = azure_openai_client.embeddings.create(model=model, input=batch, **kwargs)
            # The API may return items out of order; index is authoritative.
            vectors.extend(item.embedding for item in sorted(response.data, key=lambda item: item.index))
        normalized = _normalize(np.array(vectors))
        span.set_outputs({"embedding_count": len(normalized), "embedding_dim": normalized.shape[1] if len(normalized) else 0})
        return normalized


openai_small = Embedder(name="text-embedding-3-small", dim=1536, encode=_openai_encode)


# ============================================================================================================
#                                       Embedder Registry
# ============================================================================================================
""" 
Each embedding model needs a separate pgvector table because vector dimensions
are fixed when the PostgreSQL column is created.
"""

EMBEDDERS = [openai_small, minilm]

EMBEDDING_TABLES = {"all-MiniLM-L6-v2": "chunk_emb_minilm", "text-embedding-3-small": "chunk_emb_oai"}


def embedding_table(embedder):
    """Return the SQL-safe pgvector table identifier for an embedder."""
    return sql.Identifier(EMBEDDING_TABLES[embedder.name])
