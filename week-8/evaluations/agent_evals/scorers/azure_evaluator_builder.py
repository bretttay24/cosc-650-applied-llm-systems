"""Build local Azure AI evaluators backed by a hosted judge model."""

import os
from functools import lru_cache
from importlib import import_module
from typing import Any

from azure.identity import DefaultAzureCredential

JUDGE_MODEL = os.getenv("FOUNDRY_JUDGE_MODEL", "gpt-5.6-luna")
JUDGE_THRESHOLD = 4
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")


def build_judge_model_config() -> Any:
    """Build an Azure OpenAI judge configuration without Foundry project tracking."""
    try:
        evaluation = import_module("azure.ai.evaluation")
    except ImportError as error:
        raise RuntimeError(
            "azure-ai-evaluation is not installed. Its current pandas<3 requirement conflicts with this project's pandas>=3 constraint; resolve that dependency before running Azure judges."
        ) from error

    resource_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"].split("/api/projects", maxsplit=1)[0]
    return evaluation.AzureOpenAIModelConfiguration(
        azure_endpoint=resource_endpoint, azure_deployment=JUDGE_MODEL, credential=DefaultAzureCredential(), api_version=AZURE_OPENAI_API_VERSION
    )


@lru_cache(maxsize=1)
def build_azure_evaluators(threshold: int = JUDGE_THRESHOLD) -> dict[str, Any]:
    """Create local quality evaluators backed only by the configured judge deployment."""
    try:
        evaluation = import_module("azure.ai.evaluation")
    except ImportError as error:
        raise RuntimeError("Install a compatible azure-ai-evaluation release before constructing Azure judges.") from error

    model_config = build_judge_model_config()
    return {
        "groundedness": evaluation.GroundednessEvaluator(model_config=model_config, threshold=threshold),
        "relevance": evaluation.RelevanceEvaluator(model_config=model_config, threshold=threshold),
        "tool_call_accuracy": evaluation.ToolCallAccuracyEvaluator(model_config=model_config, threshold=threshold),
    }


def get_azure_evaluator(name: str) -> Any:
    """Return one cached local Azure evaluator by name."""
    evaluators = build_azure_evaluators()
    if name not in evaluators:
        raise KeyError(f"Unknown Azure evaluator: {name}")
    return evaluators[name]
