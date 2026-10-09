---

title: Evaluation | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/agents/evaluation
description: Learn how to evaluate agents and workflows in Agent Framework using local checks, custom evaluators, and Microsoft Foundry.
author: bentho
ms.date: 2026-05-27T00:00:00.0000000Z

---

# Evaluation | Microsoft Learn

Agent Framework includes a built-in evaluation framework that lets you measure agent quality, safety, and correctness. You can run fast local checks during development, use Microsoft Foundry's cloud-based evaluators for production-grade assessment, or combine both in a single evaluation run.

The evaluation framework is designed around a few key principles:

- **Provider-agnostic** — Core evaluation types and orchestration functions work with any evaluation provider.
- **Zero friction** — Go from "I have an agent" to "I have eval results" with minimal code.
- **Progressive disclosure** — Simple scenarios require near-zero code. Advanced scenarios build on the same primitives.

## Core concepts

The evaluation framework is built on three types:

| Type | Purpose |
| --- | --- |
| **EvalItem** | A single item to evaluate — wraps the full conversation and derives query/response via a split strategy. |
| **Evaluator** | A provider that scores items — local checks, Microsoft Foundry, or any custom implementation. |
| **EvalResults** | Aggregated results from an evaluation run — pass/fail counts, per-item detail, and optional portal links. |

In Python, the evaluation framework is part of the core `agent_framework` package. Evaluators implement the `Evaluator` protocol, and orchestration is provided through `evaluate_agent()` and `evaluate_workflow()` functions.

```python
from agent_framework import (
    evaluate_agent,
    evaluate_workflow,
    EvalItem,
    EvalResults,
    LocalEvaluator,
)
```

## Local evaluators

`LocalEvaluator` runs checks locally without API calls — ideal for inner-loop development, CI smoke tests, and fast iteration. It accepts any number of check functions and applies each one to every item.

### Built-in checks

Agent Framework ships with built-in checks for common scenarios:

| Check | What it does |
| --- | --- |
| `keyword_check(*keywords)` | Response must contain all specified keywords |
| `tool_called_check(*tool_names)` | Agent must have called the specified tools |
| `tool_calls_present` | All `expected_tool_calls` names appear in the conversation (unordered, extras OK) |
| `tool_call_args_match` | Expected tool calls match on name and arguments (subset match on args) |

```python
from agent_framework import (
    LocalEvaluator,
    keyword_check,
    tool_called_check,
    tool_calls_present,
    tool_call_args_match,
)

local = LocalEvaluator(
    keyword_check("weather", "temperature"),  # Response must contain these keywords
    tool_called_check("get_weather"),  # Agent must have called this tool
    tool_calls_present,  # All expected tool call names were made
    tool_call_args_match,  # Expected tool calls match on name + args
)
```

### Custom function evaluators

Use the `@evaluator` decorator to wrap any function as an evaluator check. The function's **parameter names** determine what data it receives from the `EvalItem`:

```python
from agent_framework import evaluator, LocalEvaluator


@evaluator
def is_concise(response: str) -> bool:
    """Check response is under 500 words."""
    return len(response.split()) < 500


@evaluator
def mentions_city(response: str, expected_output: str) -> bool:
    """Check response contains the expected city name."""
    return expected_output.lower() in response.lower()


@evaluator
def used_tools(conversation: list, tools: list) -> float:
    """Score based on tool usage. Returns 0.0–1.0 (>= 0.5 passes)."""
    tool_calls = [
        c for m in conversation for c in (m.contents or []) if c.type == "function_call"
    ]
    return min(len(tool_calls) / max(len(tools), 1), 1.0)


local = LocalEvaluator(is_concise, mentions_city, used_tools)
```

Supported parameter names: `query`, `response`, `expected_output`, `expected_tool_calls`, `conversation`, `tools`, `context`.

Return types: `bool`, `float` (≥ 0.5 = pass), `dict` with `score` or `passed` key, or `CheckResult`. Async functions are handled automatically.

## Microsoft Foundry evaluators

`FoundryEvals` connects to [Microsoft Foundry's evaluation service](/en-us/azure/ai-foundry/concepts/evaluation-approach-gen-ai) for cloud-based LLM-as-judge evaluation. Results are viewable in the Foundry portal with dashboards and comparison views.

For project setup, trace evaluation, rubric evaluators, and runnable service-specific samples, see [Microsoft Foundry evaluation](../integrations/by-component/evaluation/microsoft-foundry).

```python
from agent_framework.foundry import FoundryEvals

evals = FoundryEvals(
    project_client=project_client,
    model="gpt-4o",
    evaluators=[FoundryEvals.RELEVANCE, FoundryEvals.COHERENCE],
)
```

By default, `FoundryEvals` runs **relevance**, **coherence**, and **task adherence** evaluators. When items contain tool definitions, it automatically adds **tool call accuracy**.

### Available evaluators

`FoundryEvals` provides constants for all built-in evaluator names:

| Category | Evaluators |
| --- | --- |
| **Agent behavior** | `intent_resolution`, `task_adherence`, `task_completion`, `task_navigation_efficiency` |
| **Tool usage** | `tool_call_accuracy`, `tool_selection`, `tool_input_accuracy`, `tool_output_utilization`, `tool_call_success` |
| **Quality** | `coherence`, `fluency`, `relevance`, `groundedness`, `response_completeness`, `similarity` |
| **Safety** | `violence`, `sexual`, `self_harm`, `hate_unfairness` |

Note

`FoundryEvals` requires a Microsoft Foundry project with an AI model deployment. The `model` parameter specifies which model to use as the LLM judge.

## Evaluate an agent

The simplest evaluation scenario runs an agent against test queries and scores the responses. Provide multiple diverse queries for statistically meaningful evaluation.

```python
from agent_framework import evaluate_agent
from agent_framework.foundry import FoundryEvals

evals = FoundryEvals(
    project_client=project_client,
    model="gpt-4o",
    evaluators=[FoundryEvals.RELEVANCE, FoundryEvals.COHERENCE],
)

results = await evaluate_agent(
    agent=my_agent,
    queries=[
        "What's the weather in Seattle?",
        "Plan a weekend trip to Portland",
        "What restaurants are near Pike Place?",
    ],
    evaluators=evals,
)

for r in results:
    print(f"{r.provider}: {r.passed}/{r.total}")
    r.raise_for_status()  # Raises EvalNotPassedError if any item failed
```

`evaluate_agent` runs the agent once per query, converts each interaction to an `EvalItem`, and passes the batch to the evaluator. It returns one `EvalResults` per evaluator provider.


### Measure consistency with repetitions

Run each query multiple times to detect non-deterministic behavior:

```python
results = await evaluate_agent(
    agent=my_agent,
    queries=["What's the weather in Seattle?"],
    evaluators=evals,
    num_repetitions=3,  # Each query runs 3 times independently
)
# Results contain 3 items (1 query × 3 repetitions)
```

## Evaluate with expected outputs

Provide ground-truth expected answers to evaluate correctness. Expected outputs are paired positionally with queries:

```python
from agent_framework import evaluate_agent, ExpectedToolCall

results = await evaluate_agent(
    agent=my_agent,
    queries=["What's 2+2?", "Capital of France?"],
    expected_output=["4", "Paris"],
    evaluators=evals,
)
```

You can also specify expected tool calls:

```python
results = await evaluate_agent(
    agent=my_agent,
    queries=["What's the weather in NYC?"],
    expected_tool_calls=[ExpectedToolCall("get_weather", {"location": "NYC"})],
    evaluators=local,
)
```

## Evaluate pre-existing responses

When you already have agent responses from logs or previous runs, evaluate them directly without re-running the agent:

```python
from agent_framework import Message, evaluate_agent

response = await agent.run([Message("user", ["What's the weather?"])])

results = await evaluate_agent(
    agent=agent,
    responses=response,
    queries="What's the weather?",
    evaluators=evals,
)
```

## Conversation split strategies

Multi-turn conversations must be split into query and response halves for evaluation. How you split determines *what you're evaluating*.

| Strategy | Behavior | Best for |
| --- | --- | --- |
| **Last turn** (default) | Split at the last user message. Everything up to it is query context; everything after is the response. | Response quality at a specific point |
| **Full** | First user message is the query; the entire remainder is the response. | Task completion and overall trajectory |
| **Per-turn** | Each user→assistant exchange is scored independently with cumulative context. | Fine-grained analysis |


```python
from agent_framework import evaluate_agent, ConversationSplit

# Full conversation as context
results = await evaluate_agent(
    agent=agent,
    queries=["Plan a 3-day trip to Paris"],
    evaluators=evals,
    conversation_split=ConversationSplit.FULL,
)

# Per-turn: each exchange scored independently
from agent_framework import EvalItem

items = EvalItem.per_turn_items(conversation)
# Pass items directly to an evaluator
per_turn_results = await evaluator.evaluate(items)
```

You can also provide a custom splitter — any callable that takes a conversation and returns `(query_messages, response_messages)`:

```python
def split_before_memory(conversation):
    """Split just before a memory-retrieval tool call."""
    for i, msg in enumerate(conversation):
        for c in msg.contents or []:
            if c.type == "function_call" and c.name == "retrieve_memory":
                return conversation[:i], conversation[i:]
    # Fallback to default
    return EvalItem._split_last_turn_static(conversation)


results = await evaluate_agent(
    agent=agent,
    queries=queries,
    evaluators=evals,
    conversation_split=split_before_memory,
)
```

## Evaluate workflows

Evaluate multi-agent workflows with per-agent breakdown. The framework extracts each sub-agent's interactions and evaluates them individually, along with the workflow's overall output.

```python
from agent_framework import evaluate_workflow
from agent_framework.foundry import FoundryEvals

evals = FoundryEvals(project_client=project_client, model="gpt-4o")
result = await workflow.run("Plan a trip to Paris")

eval_results = await evaluate_workflow(
    workflow=workflow,
    workflow_result=result,
    evaluators=evals,
)

for r in eval_results:
    print(f"{r.provider}: {r.passed}/{r.total}")
    for name, sub in r.sub_results.items():
        print(f"  {name}: {sub.passed}/{sub.total}")
```

You can also pass `queries` directly and the framework will run the workflow for you:

```python
eval_results = await evaluate_workflow(
    workflow=workflow,
    queries=["Plan a trip to Paris", "Book a flight to London"],
    evaluators=evals,
)
```

## Mix multiple evaluators

Run local checks and cloud-based evaluators together in a single evaluation. Each evaluator produces its own `EvalResults`.

```python
from agent_framework import evaluate_agent, evaluator, LocalEvaluator, keyword_check
from agent_framework.foundry import FoundryEvals


@evaluator
def is_helpful(response: str) -> bool:
    return len(response.split()) > 10


foundry = FoundryEvals(
    project_client=project_client,
    model="gpt-4o",
    evaluators=[FoundryEvals.RELEVANCE, FoundryEvals.COHERENCE],
)

results = await evaluate_agent(
    agent=agent,
    queries=["What's the weather in Seattle?"],
    evaluators=[
        LocalEvaluator(is_helpful, keyword_check("weather")),
        foundry,
    ],
)

# results[0] = local evaluator results
# results[1] = Foundry evaluator results
for r in results:
    print(f"{r.provider}: {r.passed}/{r.total}")
```