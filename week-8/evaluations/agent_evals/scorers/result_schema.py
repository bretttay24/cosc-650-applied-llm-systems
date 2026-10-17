"""Schema and parsing helpers for Azure AI evaluator result dictionaries."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class AzureEvaluationResultSchema:
    """Normalized score fields returned by an Azure evaluator."""

    score: float | int | bool | str
    rationale: str | None
    threshold: float | int | None
    result: str | bool | None
    raw: Mapping[str, Any]


def parse_azure_result(result: Mapping[str, Any], metric: str) -> AzureEvaluationResultSchema:
    """Extract current or legacy score fields for one Azure evaluator metric."""
    score_keys = (metric, f"{metric}_score", f"gpt_{metric}", "score")
    score_key = next((key for key in score_keys if result.get(key) is not None), None)
    if score_key is None:
        raise KeyError(f"Azure evaluator result has no score for {metric!r}: {sorted(result)}")

    rationale = result.get(f"{metric}_reason", result.get("reason"))
    if rationale is not None and not isinstance(rationale, str):
        rationale = str(rationale)

    return AzureEvaluationResultSchema(
        score=result[score_key],
        rationale=rationale,
        threshold=result.get(f"{metric}_threshold", result.get("threshold")),
        result=result.get(f"{metric}_result", result.get("result")),
        raw=result,
    )
