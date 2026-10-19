# Imports
import re
from dataclasses import dataclass, field

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


@dataclass
class Chunk:
    text: str
    source: str  # week-5/Docs/Neo4j.md
    chunker: str  # "md-header", "fixed-320-40", ...
    ordinal: int  # position within the doc for this chunker
    header_path: str  # "Microsoft Agent Framework Overview > Install > Python"
    meta: dict = field(default_factory=dict)  # frontmatter + anything else


# ============================================================================================================
#                                    Whole Sample Chunk
# ============================================================================================================


def chunk_whole(meta, body, source, ordinal=0):
    """Store one complete source item as one chunk without splitting it."""
    return [
        Chunk(
            text=body,
            source=source,
            chunker="whole",
            ordinal=ordinal,
            header_path="",
            meta=dict(meta),
        )
    ]


# ============================================================================================================
#                                   Fixed-Size Character Window Chunker
# ============================================================================================================

""" 
This strategy splits text into character windows. Neighboring windows share the
requested number of characters.

For example, with `body="ABCDEFGHIJKLMNOPQRSTUVWXYZ"`, `meta={}`,
`source="example.md"`, `size=10`, and `overlap=3`, the output is:
[
    Chunk(
        text="ABCDEFGHIJ",
        source="example.md",
        chunker="fixed-10-3",
        ordinal=0,
        header_path="",
        meta={"char_start": 0},
    ),
    Chunk(
        text="HIJKLMNOPQ",
        source="example.md",
        chunker="fixed-10-3",
        ordinal=1,
        header_path="",
        meta={"char_start": 7},
    ),
    Chunk(
        text="OPQRSTUVWX",
        source="example.md",
        chunker="fixed-10-3",
        ordinal=2,
        header_path="",
        meta={"char_start": 14},
    ),
    Chunk(
        text="VWXYZ",
        source="example.md",
        chunker="fixed-10-3",
        ordinal=3,
        header_path="",
        meta={"char_start": 21},
    ),
]
"""


def chunk_fixed(meta, body, source, size=320, overlap=40):
    """Baseline: header-blind character windows, whitespace collapsed."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    text = re.sub(r"\s+", " ", body).strip()
    chunker_name = f"fixed-{size}-{overlap}"
    return [
        Chunk(
            text=text[start : start + size],
            source=source,
            chunker=chunker_name,
            ordinal=ordinal,
            header_path="",
            meta={**meta, "char_start": start},
        )
        for ordinal, start in enumerate(range(0, len(text), size - overlap))
    ]


# ============================================================================================================
#                                   Markdown Header Chunker
# ============================================================================================================

""" 
This strategy creates one chunk for each Markdown header-based section. The chunk
includes the header text and is not limited to a fixed size. Its metadata includes
the Markdown header hierarchy, but does not include a character offset.

For example, with `body="# Setup\\nInstall dependencies."`, `meta={}`, and
`source="example.md"`, the output is:
[
    Chunk(
        text="# Setup\\nInstall dependencies.",
        source="example.md",
        chunker="md-header",
        ordinal=0,
        header_path="Setup",
        meta={"h1": "Setup"},
    ),
]
"""

HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def header_path_of(section) -> str:
    return " > ".join(
        section.metadata[level]
        for level in ("h1", "h2", "h3")
        if section.metadata.get(level)
    )


def chunk_markdown_header(meta, body, source):
    """One chunk per markdown section; sections are unbounded in length."""
    sections = MarkdownHeaderTextSplitter(HEADERS, strip_headers=False).split_text(body)
    return [
        Chunk(
            text=section.page_content,
            source=source,
            chunker="md-header",
            ordinal=ordinal,
            header_path=header_path_of(section),
            meta={**meta, **section.metadata},
        )
        for ordinal, section in enumerate(sections)
    ]


# ============================================================================================================
#                                   Markdown Header Recursive Chunker
# ============================================================================================================

""" 
This strategy first creates Markdown header-based sections, then splits each
section into smaller pieces. The recursive splitter prefers paragraph, line, and
word boundaries, so a chunk may be shorter than the requested size. Each chunk
retains the header hierarchy of the section it came from.

For example, with `body="# A\\nABCDEFGHIJKLMNOPQRSTUVWXYZ"`, `meta={}`,
`source="example.md"`, `size=10`, and `overlap=3`, the chunk texts are
`"# A"`, `"ABCDEFGHI"`, `"GHIJKLMNOP"`, `"NOPQRSTUVW"`, and `"UVWXYZ"`.
Every chunk has `header_path="A"` and `meta={"h1": "A"}`.
"""


def chunk_markdown_header_recursive(meta, body, source, size=800, overlap=100):
    """Header split first, then bound final chunk length recursively."""
    sections = MarkdownHeaderTextSplitter(HEADERS, strip_headers=False).split_text(body)
    sub_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap
    )

    chunks = []
    for section in sections:
        for piece in sub_splitter.split_text(section.page_content):
            chunks.append(
                Chunk(
                    text=piece,
                    source=source,
                    chunker="md-header+rec",
                    ordinal=len(chunks),
                    header_path=header_path_of(section),
                    meta={**meta, **section.metadata},
                )
            )
    return chunks


CHUNKERS = {
    "whole": chunk_whole,
    "fixed-320-40": chunk_fixed,
    "md-header": chunk_markdown_header,
    "md-header+rec": chunk_markdown_header_recursive,
}
