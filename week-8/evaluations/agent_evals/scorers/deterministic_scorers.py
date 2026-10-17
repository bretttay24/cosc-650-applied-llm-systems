"""Deterministic MLflow scorers for exact capstone behavior."""

from collections.abc import Mapping, Sequence
from typing import Any

from mlflow.entities import Feedback
from mlflow.genai import scorer


def _tool_names(tool_calls: Sequence[str | Mapping[str, Any]]) -> list[str]:
    names = []
    for call in tool_calls:
        if isinstance(call, str):
            names.append(call)
            continue
        name = call.get("name")
        if name is None and isinstance(call.get("function"), Mapping):
            name = call["function"].get("name")
        if not isinstance(name, str):
            raise ValueError(f"Tool call has no string name: {call!r}")
        names.append(name)
    return names


@scorer
def label_exact_match(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Check the recorded classification label against held-out ground truth."""
    actual = outputs.get("predicted_label")
    expected = expectations.get("expected_label")
    matched = actual == expected
    return Feedback(value=matched, rationale=f"Expected {expected!r}; recorded {actual!r}.")


@scorer
def confidence_exact_match(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Check the recorded confidence against held-out ground truth."""
    actual = outputs.get("predicted_confidence")
    expected = expectations.get("expected_confidence")
    matched = actual == expected
    return Feedback(value=matched, rationale=f"Expected {expected!r}; recorded {actual!r}.")


@scorer
def retrieval_label_hit_at_3(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Check whether the expected label occurs in the first three retrieved examples."""
    expected = expectations.get("expected_label")
    labels = list(outputs.get("retrieved_labels", []))[:3]
    matched = expected in labels
    return Feedback(value=matched, rationale=f"Expected {expected!r}; retrieved labels were {labels!r}.")


@scorer
def required_tools_called(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Check that every expected tool appears in the actual tool trajectory."""
    actual = _tool_names(outputs.get("tool_calls", []))
    expected = list(expectations.get("expected_tools", []))
    missing = [name for name in expected if name not in actual]
    return Feedback(value=not missing, rationale=f"Expected {expected!r}; called {actual!r}; missing {missing!r}.")


@scorer
def tool_order_match(outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Check that the tool trajectory exactly matches the expected sequence."""
    actual = _tool_names(outputs.get("tool_calls", []))
    expected = list(expectations.get("expected_tools", []))
    return Feedback(value=actual == expected, rationale=f"Expected order {expected!r}; observed {actual!r}.")
