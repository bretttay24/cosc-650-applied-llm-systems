---
name: azure-ai-evals-mlflow
description: "Build or update local Python evaluations that use Azure AI Evaluation SDK evaluators with judge models hosted in Microsoft Foundry, then store scores only in MLflow. Use for azure-ai-evaluation, local Foundry-model judges, MLflow @scorer adapters, trace feedback, groundedness, relevance, tool-call accuracy, or evaluating local/hosted agents without creating Foundry portal evaluation runs. Do not use for Foundry cloud evaluation tracking, hosted batch eval jobs, deployment, or production monitoring."
license: MIT
metadata:
  author: Brett Taylor
  version: "1.0"
---

# Azure AI Evaluations with MLflow

Build evaluation code where execution and result tracking remain local to the application and MLflow, while Azure-hosted model deployments provide judge inference.

## Required Architecture

```text
local or hosted agent response
    -> MLflow trace
    -> local azure-ai-evaluation evaluator
    -> Azure-hosted judge model inference
    -> MLflow Feedback / scorer result
```

Foundry hosts the judge model only. It must not own or track the evaluation run.

## Hard Boundaries

- Use evaluators from `azure.ai.evaluation` locally.
- Use `AzureOpenAIModelConfiguration` with the Azure resource endpoint and deployment name.
- Use Microsoft Entra authentication through `DefaultAzureCredential` when supported by the installed SDK.
- Omit `azure_ai_project` from `azure.ai.evaluation.evaluate(...)`.
- Do not use `agent_framework.foundry.FoundryEvals`; it submits managed evaluations and returns a Foundry portal report URL.
- Do not use `AIProjectClient` cloud evaluation creation/run APIs.
- Do not upload datasets or evaluation results to Foundry.
- Do not use evaluators that require the Foundry backend service, including safety evaluators and `GroundednessProEvaluator`, when no Foundry tracking/service execution is allowed.
- Store per-trace scores, reasons, model identity, and evaluator version in MLflow.
- Do not add report-image generation unless the user separately requests it.

## Workflow

### 1. Inspect Before Editing

Read:

1. The evaluation plan and held-out dataset.
2. Agent construction and invocation code.
3. MLflow tracking and trace destination setup.
4. Existing trace span names and output contracts.
5. Installed versions of `azure-ai-evaluation`, `mlflow`, `azure-identity`, and `agent-framework`.

If `azure-ai-evaluation` is absent, add it with UV. Do not install it ad hoc with bare `pip` in this repository.

### 2. Choose the Evaluation Path

Use one of these paths:

| Situation | Path |
| --- | --- |
| One response or a few spot checks | Call evaluator instances directly and log their returned scores with `mlflow.log_feedback` |
| Batch of existing MLflow traces | Use `mlflow.genai.evaluate(data=traces, scorers=[...])` with Azure evaluator adapters decorated by `@scorer` |
| Static responses without traces | Use `mlflow.genai.evaluate` with rows containing `inputs`, `outputs`, and `expectations`; scorers must not require `trace` |
| Hosted agent response | Invoke the hosted agent normally, capture or create an MLflow trace locally, then run the same local evaluator adapters |

Never switch to Foundry cloud evaluation merely because the candidate agent is hosted.

### 3. Configure the Judge Model

Follow [the verified syntax reference](./references/local-evaluation-syntax.md). Use the Azure resource endpoint, not the project-scoped endpoint ending in `/api/projects/<project>`.

In this repository, derive the resource endpoint consistently with the existing application:

```python
resource_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"].split("/api/projects", maxsplit=1)[0]
```

Keep the judge deployment separate from the generation deployment through an environment variable such as `FOUNDRY_JUDGE_MODEL`.

### 4. Select Minimal Evaluators

Prefer deterministic scoring when exact behavior is observable.

| Need | Preferred scorer |
| --- | --- |
| Exact classification label | MLflow code scorer |
| Tool name, arguments, order, or success | MLflow code scorer |
| Rationale supported by patient comment/context | `GroundednessEvaluator` adapter |
| Response addresses the request | `RelevanceEvaluator` adapter |
| Semantic tool choice/arguments | `ToolCallAccuracyEvaluator` adapter |
| Exact expected tool sequence | MLflow code scorer, not an LLM judge |

Limit capstone-facing LLM dimensions to two or three. Do not instantiate broad evaluator suites by default.

### 5. Connect Azure Results to MLflow

Use one of the two supported patterns in [the syntax reference](./references/local-evaluation-syntax.md):

- Return `Feedback` from an MLflow `@scorer` adapter.
- Attach externally computed evaluator results to an existing trace with `mlflow.log_feedback`.

Always set the assessment source to `AssessmentSourceType.LLM_JUDGE` and include a specific `source_id` containing the Azure evaluator and judge deployment.

Keep score names stable, for example:

- `azure_groundedness`
- `azure_relevance`
- `azure_tool_call_accuracy`

Store the evaluator reason as the MLflow feedback rationale. Include the raw result-key names and judge deployment in metadata when useful.

### 6. Preserve One Candidate Execution

Run the candidate agent once per case. Reuse its stored response and trace for every evaluator.

Do not let each judge rerun the candidate agent. Judge-model calls are separate evaluation inference and should not mutate the agent session ledger.

### 7. Validate

Before a full batch:

1. Run one evaluator against one known case.
2. Confirm the returned dictionary contains the expected score and reason keys.
3. Confirm no Foundry report URL or cloud evaluation ID is produced.
4. Confirm no `azure_ai_project` argument is present.
5. Confirm the feedback appears on the intended MLflow trace.
6. Confirm the feedback source is `LLM_JUDGE` and identifies the Azure evaluator/deployment.
7. Run one failing case to ensure rationale and errors remain inspectable.

Then run the smallest relevant test or evaluation subset before the full held-out set.

## Result Ownership

Expected result locations:

- Candidate traces: MLflow experiment.
- Deterministic scores: MLflow evaluation results or trace feedback.
- Azure evaluator scores and reasons: MLflow trace feedback.
- Optional local JSON/JSONL exports: repository evaluation output directory.
- Foundry portal evaluation records: none.

Model-provider request telemetry and Azure platform logs may still exist according to the Azure resource configuration. This skill prevents creation of Foundry evaluation runs and portal evaluation reports; it does not disable ordinary service-side model inference diagnostics.

## Version Safety

Azure evaluation APIs evolve quickly. Before generating implementation code:

1. Check the installed package version.
2. Inspect callable signatures or current official API reference for that version.
3. Prefer stable non-preview evaluator classes.
4. Mark experimental classes such as `ToolCallAccuracyEvaluator` where applicable.
5. Never copy classic `azure_ai_project` upload examples into this no-portal workflow.

## Completion Checklist

- [ ] `azure-ai-evaluation` is managed by UV.
- [ ] Evaluators run in the local Python process.
- [ ] Judge inference uses the Azure/Foundry-hosted deployment.
- [ ] `azure_ai_project` is omitted.
- [ ] `FoundryEvals` and cloud evaluation APIs are absent.
- [ ] Candidate responses are generated once.
- [ ] Azure scores and reasons appear in MLflow.
- [ ] Feedback source identifies an LLM judge.
- [ ] No Foundry evaluation run or report URL is created.
- [ ] Focused validation passes.
