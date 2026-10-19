"""Validate and load HCAHPS training examples into local pgvector."""

import json
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv


DATA_DIRECTORY = Path(__file__).resolve().parent
WEEK_DIRECTORY = DATA_DIRECTORY.parent
REPOSITORY_ROOT = WEEK_DIRECTORY.parent
TRAINING_DATA_PATH = DATA_DIRECTORY / "hcahps_synthetic_train.jsonl"
TRAINING_RAG_SOURCE = "week-8:hcahps-training-examples"
TRAINING_CHUNKER = "hcahps-training-example"
CLASSIFICATION_PREFIX = "Classify this patient comment:"
SUPPORTED_LABELS = {
    "communication_nurses",
    "communication_doctors",
    "staff_responsiveness",
    "communication_medicines",
    "discharge_information",
    "care_transition",
    "cleanliness",
    "quietness",
    "other",
}
SUPPORTED_CONFIDENCE = {"low", "medium", "high"}
ANSWER_FIELDS = {"label", "rationale", "confidence"}


def read_jsonl_with_report(data_path: Path) -> tuple[list[object], Counter]:
    """Read the original JSONL file and report blank or malformed lines."""
    if not data_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    records = []
    report = Counter()
    with data_path.open(encoding="utf-8") as input_file:
        for line in input_file:
            report["lines_seen"] += 1
            if not line.strip():
                report["blank_lines"] += 1
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                report["malformed_json"] += 1

    report["records_read"] = len(records)
    return records, report


def _message_text(sample: dict[str, object], role: str) -> str:
    """Return the first non-empty message text for the requested role."""
    messages = sample.get("messages")
    if not isinstance(messages, list):
        return ""

    for message in messages:
        if isinstance(message, dict) and message.get("role") == role and isinstance(message.get("content"), str) and message["content"].strip():
            return message["content"].strip()
    return ""


def _filter_samples(samples: list[object]) -> tuple[list[dict[str, object]], Counter]:
    """Keep records with a non-empty user query and assistant answer."""
    filtered_data = []
    report = Counter()

    for sample in samples:
        if not isinstance(sample, dict):
            report["not_json_object"] += 1
        elif not _message_text(sample, "user") or not _message_text(sample, "assistant"):
            report["missing_query_or_answer"] += 1
        else:
            filtered_data.append(sample)

    return filtered_data, report


def _deduplicate_samples(samples: list[dict[str, object]]) -> tuple[list[dict[str, object]], int]:
    """Remove duplicate query-answer pairs, ignoring case and whitespace."""
    unique_data = []
    seen_pairs = set()
    duplicate_count = 0

    for sample in samples:
        query = " ".join(_message_text(sample, "user").casefold().split())
        answer = " ".join(_message_text(sample, "assistant").casefold().split())
        pair = (query, answer)
        if pair in seen_pairs:
            duplicate_count += 1
            continue
        seen_pairs.add(pair)
        unique_data.append(sample)

    return unique_data, duplicate_count


def _validate_samples(samples: list[dict[str, object]]) -> tuple[list[dict[str, object]], Counter]:
    """Require valid user-assistant classification samples."""
    valid_data = []
    report = Counter()
    expected_roles = ["user", "assistant"]

    for sample in samples:
        messages = sample.get("messages")
        roles = [message.get("role") if isinstance(message, dict) else None for message in messages] if isinstance(messages, list) else []
        contents_valid = isinstance(messages, list) and all(
            isinstance(message, dict) and isinstance(message.get("content"), str) and bool(message["content"].strip()) for message in messages
        )

        try:
            query = _message_text(sample, "user")
            answer = json.loads(_message_text(sample, "assistant"))
            answer_valid = (
                isinstance(answer, dict)
                and set(answer) == ANSWER_FIELDS
                and answer.get("label") in SUPPORTED_LABELS
                and answer.get("confidence") in SUPPORTED_CONFIDENCE
                and isinstance(answer.get("rationale"), str)
                and bool(answer["rationale"].strip())
            )
        except json.JSONDecodeError:
            query = ""
            answer_valid = False

        if (
            set(sample) != {"messages"}
            or roles != expected_roles
            or not contents_valid
            or not query.startswith(CLASSIFICATION_PREFIX)
            or not query.removeprefix(CLASSIFICATION_PREFIX).strip()
            or not answer_valid
        ):
            report["invalid_message_format"] += 1
        else:
            valid_data.append(sample)

    return valid_data, report


def clean_and_validate_data(data_path: Path = TRAINING_DATA_PATH) -> list[dict[str, object]]:
    """Run the Week 7 quality-check sequence before loading the database."""
    raw_data, read_report = read_jsonl_with_report(data_path)
    filtered_data, filter_report = _filter_samples(raw_data)
    unique_data, duplicate_count = _deduplicate_samples(filtered_data)
    clean_data, validation_report = _validate_samples(unique_data)

    print("========================= DATA QUALITY REPORT =========================")
    print(f"JSONL lines: {read_report['lines_seen']}")
    print(f"Parsed records: {read_report['records_read']}")
    print(f"Blank lines: {read_report['blank_lines']}")
    print(f"Malformed JSON lines: {read_report['malformed_json']}")
    print(f"Filtered records: {sum(filter_report.values())}")
    print(f"Duplicate query-answer pairs: {duplicate_count}")
    print(f"Invalid formats: {sum(validation_report.values())}")
    print(f"Clean training records: {len(clean_data)}")
    print("=======================================================================")

    rejected_count = read_report["blank_lines"] + read_report["malformed_json"] + sum(filter_report.values()) + duplicate_count + sum(validation_report.values())
    if rejected_count:
        raise ValueError("Training data failed quality checks; nothing was loaded.")
    return clean_data


def format_training_sample(sample: dict[str, object]) -> str:
    """Format one complete chat sample as RAG context after retrieval."""
    return "\n\n".join(f"{message['role'].title()}: {message['content']}" for message in sample["messages"])


def load_training_examples(training_data: list[dict[str, object]]) -> tuple[int, int]:
    """Embed validated examples and replace their source rows."""
    if str(WEEK_DIRECTORY) not in sys.path:
        sys.path.insert(0, str(WEEK_DIRECTORY))

    from local_rag.rag_components.chunkers import chunk_whole
    from local_rag.rag_components.database import clear_source, connect_database, ensure_schema, write_chunks, write_embeddings
    from local_rag.rag_components.embedders import openai_small

    training_chunks = []
    for sample_index, sample in enumerate(training_data):
        query = _message_text(sample, "user")
        answer = _message_text(sample, "assistant")
        chunk = chunk_whole(
            meta={"sample_index": sample_index, "query": query, "comment": query.removeprefix(CLASSIFICATION_PREFIX).strip(), "answer": answer, **json.loads(answer)},
            body=format_training_sample(sample),
            source=TRAINING_RAG_SOURCE,
            ordinal=sample_index,
        )[0]
        chunk.chunker = TRAINING_CHUNKER
        training_chunks.append(chunk)

    load_dotenv(REPOSITORY_ROOT / ".env")
    with connect_database() as connection:
        ensure_schema(connection, [openai_small])
        clear_source(connection, TRAINING_RAG_SOURCE)
        chunk_count = write_chunks(connection, training_chunks)
        vector_count = write_embeddings(connection, openai_small, training_chunks, text_for_embedding=lambda chunk: chunk.meta["comment"])
    return chunk_count, vector_count


def main() -> None:
    training_data = clean_and_validate_data()
    chunk_count, vector_count = load_training_examples(training_data)
    print(f"Loaded {chunk_count} chunks and {vector_count} text-embedding-3-small vectors.")


if __name__ == "__main__":
    main()
