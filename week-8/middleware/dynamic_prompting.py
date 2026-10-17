"""Agent middleware that adds retrieved examples to classification requests."""

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

import mlflow
from agent_framework import AgentContext, AgentMiddleware, Message
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from mlflow.entities import SpanType
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()

ENABLE_SENSITIVE_DATA = os.getenv("ENABLE_SENSITIVE_DATA", "false").lower() == "true"
CLASSIFICATION_THRESHOLD = 0.5
DECISION_MODEL = "Decision-1"
DECISION_TIMEOUT_SECONDS = 30.0
RETRIEVAL_TIMEOUT_SECONDS = 30.0
RETRIEVAL_COUNT = 5
FINAL_EXAMPLE_COUNT = 3
EMBEDDER_NAME = "text-embedding-3-small"
TRAINING_CHUNKER = "hcahps-training-example"
CLASSIFICATION_PREFIX = "Classify this patient comment:"
TOKEN_SCOPE = "https://ai.azure.com/.default"
FOUNDRY_PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"].rstrip("/")
RESOURCE_ENDPOINT = FOUNDRY_PROJECT_ENDPOINT.split("/api/projects", maxsplit=1)[0]
DECISION_ENDPOINT = f"{RESOURCE_ENDPOINT}/providers/microsoft"

LOGGER = logging.getLogger(__name__)


def _call_decision_api(query: str) -> float:
    with DefaultAzureCredential() as credential:
        token_provider = get_bearer_token_provider(credential, TOKEN_SCOPE)
        with (
            TypeSafeClient(api_key=token_provider(), base_url=DECISION_ENDPOINT, model=DECISION_MODEL, timeout=DECISION_TIMEOUT_SECONDS) as client,
            mlflow.start_span(name="decision_model_call", span_type=SpanType.LLM) as span,
        ):
            span.set_inputs({"text": query, "model": DECISION_MODEL})
            response = client.system_one(
                state=query, questions={"needs_classification": Noul(instructions="Is this user query asking for a classification task, or does it need classification?")}
            )
            token_usage = {key: value for key, value in {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}.items() if value is not None}
            if token_usage:
                token_usage["total_tokens"] = sum(token_usage.values())
                span.set_attributes({"mlflow.chat.tokenUsage": token_usage, "mlflow.llm.model": response.model})
            classification_request_probability = float(response.nouls["needs_classification"].noul)
            span.set_outputs({"needs_classification": {"probability": classification_request_probability}})

    if not 0.0 <= classification_request_probability <= 1.0:
        raise ValueError("Decision-1 returned a probability outside [0, 1]")
    return classification_request_probability


async def classification_probability(query: str) -> float:
    """Return Decision-1's calibrated probability that the query needs classification."""
    return await asyncio.wait_for(asyncio.to_thread(_call_decision_api, query), timeout=DECISION_TIMEOUT_SECONDS + 1.0)


def _retrieve_sync(query: str) -> list[dict[str, Any]]:
    """Retrieve examples through the existing local RAG pipeline."""
    from local_rag.rag_components.database import connect_database
    from local_rag.retrievers import retrieve

    search_query = query.removeprefix(CLASSIFICATION_PREFIX).strip()
    with connect_database() as connection:
        results = retrieve(
            connection,
            search_query,
            embedders=EMBEDDER_NAME,
            chunkers=TRAINING_CHUNKER,
            retrieval_k=RETRIEVAL_COUNT,
            pool_k=RETRIEVAL_COUNT,
            final_k=FINAL_EXAMPLE_COUNT,
            jev_rerank=True,
        )
    return results[EMBEDDER_NAME]


def format_enriched_query(query: str, examples: list[dict[str, Any]]) -> str:
    """Format retrieved query/answer pairs as delimited few-shot context."""
    sections = ["=== DYNAMIC FEW-SHOT CLASSIFICATION EXAMPLES ==="]
    for index, candidate in enumerate(examples, start=1):
        sections.append(f"--- Example {index} ---\nQuery:\n{candidate['meta']['query']}\nAnswer:\n{candidate['meta']['answer']}")
    sections.append(f"=== END FEW-SHOT EXAMPLES ===\n\n=== ORIGINAL USER QUERY ===\n{query}\n=== END ORIGINAL USER QUERY ===")
    return "\n\n".join(sections)


class DynamicPromptingMiddleware(AgentMiddleware):
    """Enrich classification requests with similar examples before agent execution."""

    async def process(self, context: AgentContext, call_next: Callable[[], Awaitable[None]]) -> None:
        query: str | None = None
        classification_request_probability: float | None = None
        threshold_met = False
        final_ids: list[str] = []
        enriched = False

        try:
            with mlflow.start_span(name="dynamic_prompting", span_type=SpanType.CHAIN) as span:
                last_message = context.messages[-1] if context.messages else None
                span.set_inputs({"message_count": len(context.messages), "last_message_role": last_message.role if last_message is not None else None})

                try:
                    if last_message is None or last_message.role != "user" or not last_message.text:
                        return

                    query = last_message.text
                    span.set_attributes({"query_length": len(query), "classification_request_threshold": CLASSIFICATION_THRESHOLD})
                    classification_request_probability = await classification_probability(query)
                    threshold_met = classification_request_probability >= CLASSIFICATION_THRESHOLD
                    if not threshold_met:
                        return

                    final_examples = await asyncio.wait_for(asyncio.to_thread(_retrieve_sync, query), timeout=RETRIEVAL_TIMEOUT_SECONDS)
                    final_ids = [str(candidate.get("chunk_uid", "")) for candidate in final_examples]
                    with mlflow.start_span(name="few_shot_prompt_assembly", span_type=SpanType.PARSER) as prompt_span:
                        prompt_inputs: dict[str, Any] = {"reranked_example_ids": final_ids}
                        if ENABLE_SENSITIVE_DATA:
                            prompt_inputs.update({"original_query": query, "reranked_examples": final_examples})
                        prompt_span.set_inputs(prompt_inputs)

                        enriched_query = format_enriched_query(query, final_examples)
                        prompt_outputs: dict[str, Any] = {"enriched_prompt_length": len(enriched_query)}
                        if ENABLE_SENSITIVE_DATA:
                            prompt_outputs["enriched_user_prompt"] = enriched_query
                        prompt_span.set_outputs(prompt_outputs)
                    context.messages[-1] = Message(role="user", contents=[enriched_query])
                    enriched = True

                except Exception as error:
                    span.set_attributes({"enrichment_error": type(error).__name__})
                    LOGGER.exception("Dynamic prompt enrichment failed; passing the original query through")
                finally:
                    span.set_outputs(
                        {
                            "classification_request_probability": classification_request_probability,
                            "threshold_met": threshold_met,
                            "retrieved_example_ids": final_ids,
                            "example_count": len(final_ids),
                            "enriched": enriched,
                        }
                    )
        finally:
            LOGGER.info(
                "threshold_met=%s classification_request_probability=%s dynamic_prompting query=%r final_ids=%s",
                threshold_met,
                classification_request_probability,
                query,
                final_ids,
            )
            await call_next()
