"""Load held-out classification cases as MLflow evaluation records."""

import json
from pathlib import Path
from typing import Any


def load_classification_dataset(path: str | Path) -> list[dict[str, Any]]:
    """Convert two-message classification cases into MLflow evaluation rows.

    Each JSONL line must contain one user message followed by one assistant
    message whose content is JSON with the expected label and confidence. Each
    returned row has MLflow's standard ``inputs`` and ``expectations`` keys.
    Inputs contain the unchanged user message and a stable ID required by the
    recording tool. Expectations contain the ground truth used by scorers.

    This function does not run the agent, create traces, modify the source
    message, or modify the source file.
    """
    data = []
    with Path(path).open(encoding="utf-8") as source:
        # The source file has no case IDs, so line order supplies stable IDs.
        for comment_id, line in enumerate(source, start=1):
            record = json.loads(line)
            messages = record["messages"]
            if len(messages) != 2 or messages[0]["role"] != "user" or messages[1]["role"] != "assistant":
                raise ValueError(f"case {comment_id} must contain one user and one assistant message")

            # Preserve the dataset's user message exactly as written.
            query = messages[0]["content"]

            # Preserve the expected response for MLflow's native judges, then
            # parse the same JSON string for deterministic field-level scores.
            expected_response = messages[1]["content"]
            expected = json.loads(expected_response)
            data.append(
                {
                    "inputs": {
                        # The agent uses this ID when calling record_classification.
                        "comment_id": comment_id,
                        "query": query,
                    },
                    # MLflow passes this mapping to scorers as ground truth.
                    "expectations": {
                        "expected_response": expected_response,
                        "expected_label": expected["label"],
                        "expected_confidence": expected["confidence"],
                    },
                }
            )
    return data