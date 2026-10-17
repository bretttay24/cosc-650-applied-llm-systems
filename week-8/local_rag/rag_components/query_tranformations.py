# ============================================================================================================
#                                   Generate Multiple Queries
# ============================================================================================================
import re
import sys
from pathlib import Path

WEEK_ROOT = Path(__file__).resolve().parents[2]
if str(WEEK_ROOT) not in sys.path:
    sys.path.insert(0, str(WEEK_ROOT))

from prompts.loader import load


_PREAMBLE = re.compile(r"^(here (are|is)|sure[,!]|okay|below are)", re.IGNORECASE)
_BULLET = re.compile(r"^\s*(?:[-*•–]|\d+[.)]|\(\d+\))\s*")


def generate_multiple_queries(original_query, num_queries):
    """
    Generate multiple variations of the original query.

    Args:
        original_query (str): The original query string.
        num_queries (int): The number of query variations to generate.

    Returns:
        list: A list containing the original query and its variations.
    """
    from .clients import azure_openai_client

    prompt = load("multiple-query-generator")
    rendered_prompt = prompt.text.format(
        N=num_queries,
        original_query=original_query,
    )

    response = azure_openai_client.responses.create(
        model=prompt.model,
        input=rendered_prompt,
        **prompt.params,
    )

    return _parse_queries(response.output_text)[:num_queries]


def _parse_queries(raw):
    """Clean newline-separated LLM queries and remove common list formatting."""
    if not raw:
        return []

    lines = raw.splitlines() if isinstance(raw, str) else raw
    queries = []

    for line in lines:
        text = line.strip()
        if not text or _PREAMBLE.match(text) or text.endswith(":"):
            continue

        text = _BULLET.sub("", text).strip().strip("*").strip().strip('"').strip()
        if text:
            queries.append(text)

    return queries
