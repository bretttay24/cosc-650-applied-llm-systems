# ============================================================================================================
#                                            BM25 Lexical Search
# ============================================================================================================
import re
from rank_bm25 import BM25Okapi


_BM25_CACHE = {}
_BM25_TOKEN = re.compile(r"[A-Za-z0-9]+(?:[-_./][A-Za-z0-9]+)*")
_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _tokenize_bm25(text):
    """Tokenize prose and preserve useful technical-identifier forms."""
    tokens = []

    for raw_token in _BM25_TOKEN.findall(text or ""):
        whole_token = raw_token.lower()
        tokens.append(whole_token)
        expanded = _CAMEL_BOUNDARY.sub(" ", raw_token)
        parts = re.split(r"[-_./\s]+", expanded)

        for part in parts:
            normalized_part = part.lower()
            if normalized_part and normalized_part != whole_token:
                tokens.append(normalized_part)

    return tokens


def _get_bm25_index(connection, chunkers=None):
    """Build and cache one BM25 index for each chunker selection."""
    if isinstance(chunkers, str):
        chunkers = [chunkers]

    cache_key = None if chunkers is None else tuple(sorted(set(chunkers)))

    if cache_key not in _BM25_CACHE:
        with connection.cursor() as cursor:
            rows = cursor.execute(
                """
                SELECT chunk_uid, source, chunker, header_path, content
                FROM doc_chunk
                WHERE %(chunkers)s::text[] IS NULL
                   OR chunker = ANY(%(chunkers)s::text[])
                ORDER BY chunk_uid
                """,
                {"chunkers": (list(cache_key) if cache_key is not None else None)},
            ).fetchall()

        documents = [dict(row) for row in rows]

        tokenized_corpus = [
            # Duplicate header tokens to give headings additional weight.
            _tokenize_bm25(document["header_path"]) * 2
            + _tokenize_bm25(document["content"])
            for document in documents
        ]

        model = BM25Okapi(tokenized_corpus) if documents else None
        _BM25_CACHE[cache_key] = (model, documents)

    return _BM25_CACHE[cache_key]


def clear_bm25_cache():
    """Force indexes to rebuild after doc_chunk changes."""
    _BM25_CACHE.clear()


def search_bm25(connection, query, k=10, chunkers=None):
    """Return top-k PostgreSQL chunks ranked with Okapi BM25."""
    if k < 1:
        raise ValueError("k must be at least 1")

    model, documents = _get_bm25_index(connection, chunkers)
    query_tokens = _tokenize_bm25(query)

    if model is None or not query_tokens:
        return []

    scores = model.get_scores(query_tokens)

    ranked_indices = sorted(
        (index for index, score in enumerate(scores) if score > 0),
        key=lambda index: (
            -float(scores[index]),
            documents[index]["chunk_uid"],
        ),
    )[:k]

    return [
        {
            **documents[index],
            "retriever": "bm25",
            "search_query": query,
            "retrieval_rank": rank,
            "raw_score": float(scores[index]),
        }
        for rank, index in enumerate(ranked_indices, start=1)
    ]
