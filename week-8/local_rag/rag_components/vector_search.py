"""Semantic vector search over pgvector-backed RAG chunks."""

import mlflow
from mlflow.entities import SpanType
from psycopg import sql

from .embedders import embedding_table


def search_vectors(connection, query: str, embedder, k: int = 10, chunkers=None):
    """Return top-k chunks ranked by ascending cosine distance."""
    with mlflow.start_span(name="vector_search", span_type=SpanType.RETRIEVER) as span:
        span.set_inputs({"query": query, "embedder": embedder.name, "top_k": k, "chunkers": chunkers})
        if k < 1:
            raise ValueError("k must be at least 1")

        if isinstance(chunkers, str):
            chunkers = [chunkers]
        elif chunkers is not None:
            chunkers = list(chunkers)

        statement = sql.SQL(
            """
            SELECT c.chunk_uid, c.source, c.chunker, c.header_path, c.content, c.meta,
                   e.emb <=> %(vector)s AS distance
            FROM {table} e
            JOIN doc_chunk c USING (chunk_uid)
            WHERE %(chunkers)s::text[] IS NULL
               OR c.chunker = ANY(%(chunkers)s::text[])
            ORDER BY distance
            LIMIT %(k)s
            """
        ).format(table=embedding_table(embedder))

        with connection.cursor() as cursor:
            rows = cursor.execute(statement, {"vector": embedder.encode([query])[0], "chunkers": chunkers, "k": k}).fetchall()

        results = [
            {**dict(row), "retriever": "vector", "search_query": query, "retrieval_rank": rank, "raw_score": -float(row["distance"])} for rank, row in enumerate(rows, start=1)
        ]
        span.set_outputs(
            [{"page_content": result["content"], "metadata": {"chunk_uid": result["chunk_uid"], "source": result["source"], "score": result["raw_score"]}} for result in results]
        )
        span.set_attributes({"num_results": len(results), "embedding_model": embedder.name})
        return results
