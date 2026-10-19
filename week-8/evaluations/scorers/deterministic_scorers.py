"""Deterministic MLflow scorers for exact capstone behavior."""

from typing import Any

from mlflow.entities import Feedback, Trace
from mlflow.genai import scorer


@scorer(timeout=0)
def label_exact_match(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback | None:
    """Check the recorded classification label against held-out ground truth."""
    if "expected_label" not in expectations:
        return None
    actual = outputs.get("predicted_label")
    expected = expectations.get("expected_label")
    matched = actual == expected
    return Feedback(value=matched, rationale=f"Expected {expected!r}; recorded {actual!r}.")


@scorer(timeout=0)
def confidence_exact_match(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback | None:
    """Check the recorded confidence against held-out ground truth."""
    if "expected_confidence" not in expectations:
        return None
    actual = outputs.get("predicted_confidence")
    expected = expectations.get("expected_confidence")
    matched = actual == expected
    return Feedback(value=matched, rationale=f"Expected {expected!r}; recorded {actual!r}.")


@scorer(timeout=0)
def retrieval_label_hit_at_3(trace: Trace, expectations: dict[str, Any]) -> Feedback | None:
    """Check whether the expected label occurs in the first three retrieved examples."""
    if "expected_label" not in expectations:
        return None
    expected = expectations.get("expected_label")
    middleware_spans = trace.search_spans(name="dynamic_prompting")
    labels = list(middleware_spans[-1].outputs.get("retrieved_labels", []))[:3] if middleware_spans else []
    matched = expected in labels
    return Feedback(value=matched, rationale=f"Expected {expected!r}; retrieved labels were {labels!r}.")


@scorer(timeout=0)
def retrieval_label_matches_at_3(trace: Trace, expectations: dict[str, Any]) -> Feedback | None:
    """Count expected-label examples among the first three retrieved examples."""
    if "expected_label" not in expectations:
        return None
    expected = expectations.get("expected_label")
    middleware_spans = trace.search_spans(name="dynamic_prompting")
    labels = list(middleware_spans[-1].outputs.get("retrieved_labels", []))[:3] if middleware_spans else []
    matches = sum(label == expected for label in labels)
    return Feedback(value=matches, rationale=f"Expected {expected!r}; retrieved labels were {labels!r}.")
