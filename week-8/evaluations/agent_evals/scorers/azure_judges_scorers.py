"""MLflow scorers backed by locally executed Azure AI evaluators."""

from collections.abc import Mapping
from typing import Any

from mlflow.entities import AssessmentSource, AssessmentSourceType, Feedback
from mlflow.genai import scorer

from .azure_evaluator_builder import JUDGE_MODEL, get_azure_evaluator
from .result_schema import parse_azure_result


def _source(evaluator_name: str, deployment: str) -> AssessmentSource:
    return AssessmentSource(source_type=AssessmentSourceType.LLM_JUDGE, source_id=f"azure-ai-evaluation:{evaluator_name}:{deployment}")


def _feedback(name: str, metric: str, deployment: str, result: Mapping[str, Any]) -> Feedback:
    parsed = parse_azure_result(result, metric)
    return Feedback(
        name=name,
        value=parsed.score,
        rationale=parsed.rationale,
        source=_source(metric, deployment),
        metadata={"judge_deployment": deployment, "threshold": parsed.threshold, "result": parsed.result},
    )


@scorer
def azure_groundedness(inputs: dict[str, Any], outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Score whether the response is supported by the supplied grounding context."""
    evaluator = get_azure_evaluator("groundedness")
    result = evaluator(query=inputs["query"], response=outputs["response"], context=expectations["grounding_context"])
    return _feedback("azure_groundedness", "groundedness", JUDGE_MODEL, result)


@scorer
def azure_relevance(inputs: dict[str, Any], outputs: dict[str, Any]) -> Feedback:
    """Score whether the response addresses the user query."""
    evaluator = get_azure_evaluator("relevance")
    result = evaluator(query=inputs["query"], response=outputs["response"])
    return _feedback("azure_relevance", "relevance", JUDGE_MODEL, result)


@scorer
def azure_tool_call_accuracy(inputs: dict[str, Any], outputs: dict[str, Any], expectations: dict[str, Any]) -> Feedback:
    """Score semantic tool selection and argument accuracy."""
    evaluator = get_azure_evaluator("tool_call_accuracy")
    result = evaluator(query=inputs["query"], response=outputs["response"], tool_calls=outputs["tool_calls"], tool_definitions=expectations["tool_definitions"])
    return _feedback("azure_tool_call_accuracy", "tool_call_accuracy", JUDGE_MODEL, result)
