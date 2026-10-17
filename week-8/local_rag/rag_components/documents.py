"""Document loading and chunk preparation helpers for the local RAG pipeline."""

import re
from collections.abc import Mapping
from pathlib import Path

import yaml

from .chunkers import CHUNKERS, Chunk


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def load_document(path: Path) -> tuple[dict, str]:
    """Load one Markdown document and split its front matter from its body."""
    raw_text = path.read_text(encoding="utf-8")
    matched_front_matter = FRONT_MATTER_RE.match(raw_text)

    if matched_front_matter is None:
        return {}, raw_text

    metadata = yaml.safe_load(matched_front_matter.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"front matter must be a mapping: {path}")

    return metadata, raw_text[matched_front_matter.end() :]


def load_documents(
    documents_dir: Path,
    source_prefix: str | None = None,
) -> list[tuple[str, dict, str]]:
    """Load Markdown documents into ``(source, metadata, body)`` tuples."""
    document_paths = sorted(documents_dir.glob("*.md"))
    if not document_paths:
        raise ValueError(f"no Markdown documents found in {documents_dir}")

    prefix = source_prefix.rstrip("/") if source_prefix else None
    documents = []
    for path in document_paths:
        metadata, body = load_document(path)
        source = f"{prefix}/{path.name}" if prefix else path.as_posix()
        documents.append((source, metadata, body))

    return documents


def build_chunk_configs(
    documents: list[tuple[str, dict, str]],
    chunkers: Mapping[str, object] = CHUNKERS,
) -> dict[str, list[Chunk]]:
    """Apply every configured chunker to every loaded document."""
    return {
        name: [
            chunk
            for source, metadata, body in documents
            for chunk in chunker(metadata, body, source)
        ]
        for name, chunker in chunkers.items()
    }


def flatten_chunk_configs(configs: Mapping[str, list[Chunk]]) -> list[Chunk]:
    """Return all chunks from every chunking configuration in one list."""
    return [chunk for chunks in configs.values() for chunk in chunks]


def embed_text(chunk: Chunk) -> str:
    """Build the title, header, and body text sent to an embedding model."""
    return f"{chunk.meta.get('title', '')} - {chunk.header_path}\n\n{chunk.text}"
