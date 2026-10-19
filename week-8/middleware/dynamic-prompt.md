# Dynamic Prompting Middleware

## Purpose

The dynamic prompting middleware adds relevant few-shot examples only when the agent is handling a classification request. It runs before the agent sees the final user message.

This matters because the same agent also supports summary and plot requests. Those tasks do not need classification examples. The middleware uses Decision-1 to decide whether retrieval should run instead of adding three examples to every request.

## Active Pipeline

```text
Last user message
        |
        v
Decision-1 classification gate
        |
        +-- probability below 0.5 --> keep the original request
        |
        v
Embed the patient-comment text
        |
        v
Retrieve five similar training questions
        |
        v
JEV reranks by P(relevant)
        |
        v
Add the top three complete examples to the user message
        |
        v
Continue to the agent
```

## 1. Decide Whether the Request Needs Classification

`DynamicPromptingMiddleware.process()` reads the last message in the agent context. It continues only when that message came from the user and contains text.

The middleware sends the user message to the `Decision-1` model with one question:

> Is this user query asking for a classification task, or does it need classification?

Decision-1 returns a probability from `0.0` to `1.0`. The classification threshold is `0.5`.

- A probability of `0.5` or higher starts the retrieval pipeline.
- A probability below `0.5` skips retrieval and leaves the user message unchanged.

A request to classify a patient comment should pass the gate. A request to get a summary or create a plot should fall below the threshold. In that case, the agent handles the original request without three additional few-shot examples.

This is a probabilistic decision rather than a hard-coded intent rule. A mistaken Decision-1 score could incorrectly run or skip retrieval. The middleware records the probability and threshold result in the `dynamic_prompting` MLflow span so that decision can be inspected.

## 2. Retrieve Semantically Similar Questions

For a classification request, the middleware removes the exact `Classify this patient comment:` prefix when it appears at the beginning of the query. The remaining patient-comment text becomes the search query.

The search uses `text-embedding-3-small`. The model converts the new comment into a normalized vector. PostgreSQL with pgvector compares that vector with the stored training vectors by cosine distance. The five training comments with the smallest distance become the initial candidates.

The stored vectors represent the patient-comment portion of each training question. They do not represent only the label or answer. This lets semantic similarity match comments that describe similar patient experiences even when their wording is different.

Each matching database row still contains the complete training sample:

- The original classification question
- The expected label
- The expected rationale
- The expected confidence
- The complete user and assistant text

Vector search therefore matches on the question's patient-comment meaning and returns the whole labeled sample for later use.

## 3. Rerank the Five Candidates With JEV

Semantic similarity finds comments with related language and meaning. It does not determine whether each sample is the best demonstration for the current request. JEV performs that second decision.

JEV receives the original search query and the complete text of all five candidates. For each candidate, it estimates the probability that the sample is relevant because it answers or directly addresses the query. This value is $P(\mathrm{relevant})$ and ranges from `0.0` to `1.0`.

The candidates are sorted from the highest relevance probability to the lowest. The middleware does not apply a minimum JEV threshold. It keeps the top three candidates after reranking, even when the probabilities are close or low.

### JEV Attribution

This project first explored the JEV reranker in Week 6 and reused it in Week 7. The implementation is adapted from Adrian Raudaschl's [RAG-Fusion JEV experiment](https://github.com/Raudaschl/rag-fusion/tree/master/experiments/jev-in-the-pipeline), which is licensed under MIT. That experiment builds on Adam Hevenor's [hev reranker](https://github.com/hev/reranker), which provides the original JEV reranking recipe and is licensed under Apache-2.0.

## 4. Build the Dynamic Few-Shot Prompt

The middleware formats each of the three selected samples as a complete question-and-answer example. The answer preserves the sample's label, rationale, and confidence. The original user request is placed after the examples in a clearly delimited section.

The final message has this structure:

```text
=== DYNAMIC FEW-SHOT CLASSIFICATION EXAMPLES ===
--- Example 1 ---
Query:
<matched classification question>
Answer:
<label, rationale, and confidence>

--- Example 2 ---
...

--- Example 3 ---
...
=== END FEW-SHOT EXAMPLES ===

=== ORIGINAL USER QUERY ===
<current classification request>
=== END ORIGINAL USER QUERY ===
```

The middleware replaces only the last user message with this enriched version. It then continues the normal Agent Framework pipeline. The agent receives its stable system instructions plus three examples selected for the current classification request.

## Failure Behavior

Decision, retrieval, or prompt-assembly errors do not stop the agent request. The middleware records the error type, keeps the original query, and continues to the agent without dynamic examples.

## External References

- [TypeSafe AI Jev introduction](https://docs.typesafe.ai/introduction) explains Jev and its structured System One decisions.
- [TypeSafe Noul questions](https://docs.typesafe.ai/primitives/noul) explains the `0.0` to `1.0` probability used by the classification gate and JEV reranker.
- [TypeSafe Python SDK](https://docs.typesafe.ai/sdk/python) documents `AsyncTypeSafeClient`, `TypeSafeClient`, typed questions, and responses.
- [TypeSafe reranking cookbook](https://docs.typesafe.ai/cookbooks/rerank_typesafe) demonstrates probability-based reranking with TypeSafe models.
- [Microsoft-Decision-1 in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision) documents deployment, typed questions, probabilities, and the Microsoft decision endpoint.
- [Microsoft-Decision-1 model catalog entry](https://ai.azure.com/catalog/models/Microsoft-Decision-1) links directly to the Foundry model.
- [Microsoft Agent Framework TypeSafe AI integration](https://learn.microsoft.com/agent-framework/integrations/by-provider/type-safe-ai) documents TypeSafe models and typed questions in Agent Framework Python.
- [Microsoft Agent Framework middleware](https://learn.microsoft.com/agent-framework/concepts/agents/middleware/#agent-middleware) documents `AgentMiddleware`, `AgentContext`, and `call_next()`.
- [RAG-Fusion JEV experiment](https://github.com/Raudaschl/rag-fusion/tree/master/experiments/jev-in-the-pipeline) provides Adrian Raudaschl's JEV pipeline experiment.
- [hev reranker](https://github.com/hev/reranker) provides Adam Hevenor's original JEV reranking recipe.

## Relevant Code

- [`dynamic_prompting.py`](./dynamic_prompting.py) contains the Decision-1 gate, retrieval settings, prompt assembly, and middleware control flow.
- [`load_hcahps_training_examples.py`](../data/load_hcahps_training_examples.py) validates the training samples, stores the complete examples, and embeds each patient comment.
- [`vector_search.py`](../local_rag/rag_components/vector_search.py) embeds the incoming comment and performs the pgvector cosine-distance search.
- [`rerankers.py`](../local_rag/rag_components/rerankers.py) calculates JEV relevance probabilities and returns the top-ranked candidates.