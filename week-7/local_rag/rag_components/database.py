"""PostgreSQL and pgvector persistence helpers for the local RAG pipeline."""

import hashlib
import json
import os
from collections.abc import Callable, Iterable

import psycopg
from pgvector.psycopg import register_vector
from psycopg import sql


def connect_database(database_url: str | None = None) -> psycopg.Connection:
    """Open a vector-enabled database connection with dictionary result rows."""
    connection = psycopg.connect(
        database_url or os.environ["PGVECTOR_URL"],
        row_factory=psycopg.rows.dict_row,
    )
    register_vector(connection)
    return connection


def chunk_uid(chunk) -> str:
    """Return the stable identifier for a chunk's source and position."""
    key = f"{chunk.source}|{chunk.chunker}|{chunk.ordinal}"
    return hashlib.sha256(key.encode()).hexdigest()


def _embedding_table(embedder) -> sql.Identifier:
    """Resolve a registered embedder's SQL-safe vector-table name lazily."""
    from .embedders import embedding_table

    return embedding_table(embedder)


def ensure_schema(connection, embedders: Iterable) -> None:
    """Create the shared chunk table and one vector table per embedder."""
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cursor.execute(
            """
			CREATE TABLE IF NOT EXISTS doc_chunk (
				chunk_uid   text PRIMARY KEY,
				source      text NOT NULL,
				chunker     text NOT NULL,
				ordinal     int  NOT NULL,
				header_path text NOT NULL DEFAULT '',
				content     text NOT NULL,
				n_chars     int  NOT NULL,
				meta        jsonb NOT NULL DEFAULT '{}'::jsonb
			)
			"""
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS doc_chunk_chunker_idx ON doc_chunk (chunker)"
        )

        for embedder in embedders:
            table = _embedding_table(embedder)
            cursor.execute(
                sql.SQL(
                    """
					CREATE TABLE IF NOT EXISTS {table} (
						chunk_uid   text PRIMARY KEY REFERENCES doc_chunk(chunk_uid) ON DELETE CASCADE,
						embed_input text NOT NULL,
						emb         vector({dim}) NOT NULL
					)
					"""
                ).format(table=table, dim=sql.Literal(embedder.dim))
            )
            cursor.execute(
                sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {index} ON {table} USING hnsw (emb vector_cosine_ops)"
                ).format(
                    index=sql.Identifier(f"{embedder.name}_emb_idx"),
                    table=table,
                )
            )


def clear_database(connection) -> None:
    """Remove all chunks and embeddings while preserving the schema and indexes."""
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE doc_chunk CASCADE")


def clear_source(connection, source: str) -> None:
    """Remove one source corpus and its embeddings while preserving other data."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM doc_chunk WHERE source = %s", (source,))


CHUNK_INSERT = """
INSERT INTO doc_chunk (chunk_uid, source, chunker, ordinal, header_path, content,
                       n_chars, meta)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
ON CONFLICT (chunk_uid) DO UPDATE SET
	content = EXCLUDED.content,
	n_chars = EXCLUDED.n_chars,
	meta = EXCLUDED.meta
"""


def _chunk_rows(chunks: Iterable) -> list[tuple]:
    """Translate chunks into rows for the shared ``doc_chunk`` table."""
    return [
        (
            chunk_uid(chunk),
            chunk.source,
            chunk.chunker,
            chunk.ordinal,
            chunk.header_path,
            chunk.text,
            len(chunk.text),
            json.dumps(chunk.meta, default=str),
        )
        for chunk in chunks
    ]


def write_chunks(connection, chunks: Iterable) -> int:
    """Upsert chunk text and metadata, returning the number of chunks written."""
    rows = _chunk_rows(chunks)
    if not rows:
        return 0

    with connection.cursor() as cursor:
        cursor.executemany(CHUNK_INSERT, rows)
    return len(rows)


def write_embeddings(
    connection,
    embedder,
    chunks: Iterable,
    text_for_embedding: Callable[[object], str],
) -> int:
    """Embed and upsert chunks using the caller's text representation."""
    chunk_list = list(chunks)
    if not chunk_list:
        return 0

    texts = [text_for_embedding(chunk) for chunk in chunk_list]
    vectors = embedder.encode(texts)
    rows = list(
        zip(
            [chunk_uid(chunk) for chunk in chunk_list],
            texts,
            vectors,
            strict=True,
        )
    )
    statement = sql.SQL(
        """
		INSERT INTO {table} (chunk_uid, embed_input, emb)
		VALUES (%s, %s, %s)
		ON CONFLICT (chunk_uid) DO UPDATE SET
			embed_input = EXCLUDED.embed_input,
			emb = EXCLUDED.emb
		"""
    ).format(table=_embedding_table(embedder))

    with connection.cursor() as cursor:
        cursor.executemany(statement, rows)
    return len(rows)
