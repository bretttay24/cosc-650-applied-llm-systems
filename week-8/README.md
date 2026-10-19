# Week 8: HCAHPS-Aligned Patient Feedback Agent

## Project Overview

This project builds a Microsoft Agent Framework agent that organizes
supplemental free-text patient feedback into HCAHPS-aligned themes. The agent
uses a version-controlled classification prompt, dynamically retrieved
examples, and deterministic tools for recording and summarizing its
classifications.

The system is intended to help patient-experience teams organize narrative
feedback more consistently. It is not an implementation of the official
HCAHPS survey or CMS scoring methodology.

## Supporting Documentation

| Document | Contents |
| --- | --- |
| [HCAHPS Background and Topic Definitions](./HCAHPS-info.md) | HCAHPS context, theme definitions, inclusions, and exclusions |
| [Evaluation](./evaluations/evaluation.md) | Deterministic metrics, LLM judges, score scales, and interpretation |
| [Dynamic Prompting Middleware](./middleware/dynamic-prompt.md) | Decision-1 gating, semantic retrieval, JEV reranking, and prompt enrichment |
| [Local RAG](./local_rag/README.md) | Reusable retrieval pipeline and configuration |
| [Prompt Library](./prompts/README.md) | Version-controlled prompt structure and loading |
| [Microsoft Agent Framework Toolbox](./toolbox/README.md) | Validated tools, session ledger, summaries, and visualizations |

## Problem

Official HCAHPS responses provide standardized measurements that can be
compared across hospitals, but structured response choices do not contain all
of the context behind a patient's experience. Hospitals may append
supplemental questions after the required HCAHPS items, and healthcare
organizations may collect additional narrative comments through internal
patient-experience programs.

Reviewing a large volume of comments manually is slow and can produce
inconsistent categories. This application addresses that operational problem
by:

1. Retrieving labeled examples similar to a new patient comment.
2. Supplying those examples to a classification agent.
3. Assigning one primary HCAHPS-aligned theme.
4. Recording the theme, confidence, and rationale in a session-owned ledger.
5. Summarizing or visualizing the comments processed during the session.

## Integrated Course Techniques

The project combines four components developed during earlier weeks:

- **Version-controlled prompting (Week 3):** Reuses the prompt loader,
  versioned classifier instructions, and model configuration. This keeps the
  model, parameters, and behavioral instructions reproducible as the
  classifier changes.
- **Schema-validated tool use (Week 4):** Adapts the deterministic recording,
  summary, and visualization tools for Microsoft Agent Framework with
  Pydantic-backed input validation. Tools were chosen so that the model
  interprets language while application code validates state changes and
  calculates reports.
- **Retrieval-augmented generation (Weeks 5-6):** Reuses the local vector
  retrieval pipeline to find labeled examples relevant to a patient comment.
  Retrieval supplies concrete classification examples without placing the
  complete training set in every prompt.
- **Dynamic few-shot prompting (Week 7):** Reuses the JEV reranking and
  dynamic few-shot approach to add relevant examples through agent middleware.
  The capstone adds a Decision-1 classification gate so classification
  requests receive tailored context while summary and visualization requests
  avoid unnecessary retrieval.
Together, these techniques separate subjective language interpretation from
validated tool execution and deterministic reporting while grounding each
classification in relevant examples.

## HCAHPS and the Free-Text Caveat

The Hospital Consumer Assessment of Healthcare Providers and Systems
(HCAHPS) Survey is the national, standardized, publicly reported survey of
patients' perspectives of hospital care. CMS uses required survey wording,
sampling, administration, coding, adjustment, and reporting procedures to
make hospital results comparable.

The publicly reported measures are calculated from structured responses.
This project instead analyzes supplemental narrative feedback. Its outputs
must therefore be described as **HCAHPS-aligned feedback themes**, not HCAHPS
scores.

The examples used by this project are synthetic supplemental patient-feedback
comments. They are not responses collected through an official HCAHPS survey
administration.

## Classification Scope

The classifier focuses on eight actionable care-experience themes:

1. `communication_nurses`
2. `communication_doctors`
3. `staff_responsiveness`
4. `communication_medicines`
5. `discharge_information`
6. `care_transition`
7. `cleanliness`
8. `quietness`

The `other` label is retained as a non-measure fallback for comments outside
those themes.

Detailed topic definitions, inclusions, and exclusions are documented in
[HCAHPS-info.md](./HCAHPS-info.md). The single-label boundary and confidence
rules used by the agent are maintained in the version-controlled
[classifier prompt](./prompts/hcahps-classifier/v1.txt).

### Excluded Global Measures

The project intentionally excludes:

- Overall hospital rating
- Willingness to recommend the hospital

These measures ask patients for structured assessments of the hospital as a
whole rather than identifying a specific operational topic. The classifier
does not infer an official rating or recommendation response from sentiment.
Explicit ratings, recommendation statements, and nonspecific praise or
complaints fall under `other` unless the comment also contains a supported
care-experience theme.

## System Architecture

```text
User request
  |
  v
Decision-1 classification gate
  |---------------- summary or plot request ----------------|
  |                                                         |
  v                                                         |
Embed patient comment                                        |
  |                                                         |
  v                                                         |
pgvector retrieves five examples                             |
  |                                                         |
  v                                                         |
JEV reranks and selects three                                 |
  |                                                         |
  |<--------------------------------------------------------|
  v
Version-controlled prompt + Microsoft Agent Framework agent
  |
  v
Validated recording, summary, and visualization tools
  |
  v
Session-owned classification ledger

Every integrated request -> MLflow trace
Held-out expectations + stored traces
  -> deterministic metrics + six LLM judges
  -> dashboards and failure analysis
```

### Prompt Loader

The prompt loader reads the active, version-controlled classifier prompt and
its model configuration. Stable instructions belong in the prompt:

- Supported themes
- Boundary rules
- Confidence guidance
- Tool-selection behavior
- Required rationale behavior

### Dynamic Few-Shot Retrieval

The local RAG pipeline indexes complete labeled examples. For each new
comment, retrieval selects similar examples and places them in that request's
context before the agent classifies the comment.

Retrieval occurs before classification rather than inside the recording tool.
By the time the recording tool is called, the agent has already selected a
theme. Keeping retrieval in the request orchestration also prevents the agent
from accidentally skipping an optional retrieval tool.

### Agent Tools

The deterministic tools have separate responsibilities:

- Record one already selected feedback theme.
- Summarize recorded comments by theme or model confidence.
- Visualize the recorded comment distribution.

The recording tool validates and stores the classification; it does not
classify the comment itself.

## Evaluation and Observability

The capstone evaluates 20 held-out synthetic patient comments. Each comment
runs once in a fresh Agent Framework session. The notebook attaches the
expected response, label, and confidence to that request's MLflow trace, then
evaluates the stored traces without rerunning the classifier.

The evaluation uses two complementary methods:

- **Deterministic metrics** measure exact label accuracy, confidence agreement,
  and whether the expected label appears among the three retrieved examples.
  These checks are reproducible and provide the primary ground-truth
  comparisons.
- **Six native MLflow LLM judges** assess response correctness and relevance,
  tool-call correctness and efficiency, and retrieval relevance and
  groundedness. Their written rationales provide qualitative evidence about
  failures that exact-match metrics cannot explain.

MLflow was chosen because the project needs both evaluation and observability
across an integrated agent workflow. A single trace preserves the chain,
retrieval, model, and tool spans for one request. This makes it possible to
move from an aggregate score to the retrieved examples, model response, tool
arguments, and judge explanation for the same case. Evaluating the stored
traces also avoids additional agent calls that could change the candidate
response or add unnecessary cost and latency.

The local MLflow deployment stores tracking metadata in PostgreSQL and serves
trace artifacts through the MLflow server. This keeps experiment records and
failure evidence available beyond the active notebook session. The notebook
uses the same traces for performance dashboards and for the detailed failure
analysis in Part 3.

Evaluator definitions, score scales, and the distinction between response
correctness, retrieval relevance, and retrieval groundedness are documented
in [evaluations/evaluation.md](./evaluations/evaluation.md).


## References

Official sources:

- [CMS: HCAHPS Patients' Perspectives of Care Survey](https://www.cms.gov/medicare/quality/initiatives/hospital-quality-initiative/hcahps-patients-perspectives-care-survey)
- [HCAHPS Online: Survey Instruments](https://www.hcahpsonline.org/en/survey-instruments/)
- [HCAHPS Online: Quality Assurance](https://www.hcahpsonline.org/en/quality-assurance/)
- [CMS: Hospital Value-Based Purchasing Program](https://www.cms.gov/medicare/quality/value-based-programs/hospital-purchasing)

Secondary overview:

- [Formbricks: HCAHPS survey questions - the complete 2026 guide for hospitals](https://formbricks.com/blog/hcahps-survey-questions)
