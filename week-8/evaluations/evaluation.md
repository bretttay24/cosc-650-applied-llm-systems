# Evaluation

The capstone evaluates held-out synthetic patient comments. Each comment is classified in a fresh Agent Framework session, and its expected label, confidence, and response are attached to the resulting MLflow trace. Deterministic metrics test exact application behavior. MLflow's built-in LLM judges evaluate the stored traces with `azure:/gpt-5-mini`, so the candidate agent is not run again during judge scoring.

The model is hosted through Microsoft Foundry, but the evaluators are MLflow scorers. The judge results are model-based assessments and may vary between runs.

## Score Interpretation

The metrics in this project are not scored from 0 to 5.

- A **binary metric** returns pass or fail for each case. MLflow converts pass to `1` and fail to `0`. The reported `/mean` is the number of passing assessments divided by the number evaluated.
- A **count metric** returns an integer for each case. Its `/mean` is the arithmetic mean of those counts.
- The LLM judges return `yes` or `no`. MLflow converts these values to `1` and `0` before calculating the mean pass rate.

For example, a mean of `0.95` means that 95% of the evaluated cases passed.

## Deterministic Metrics

These metrics are calculated directly from the held-out expectations, recorded tool output, and retrieved labels. They do not use an LLM judge.

| Metric | Per-case scale | Calculation | What it measures |
| --- | --- | --- | --- |
| `label_exact_match` | Pass/fail | `predicted_label == expected_label` | Exact classification-label accuracy |
| `confidence_exact_match` | Pass/fail | `predicted_confidence == expected_confidence` | Exact agreement with the expected confidence level |
| `retrieval_label_hit_at_3` | Pass/fail | Pass when at least one of the first three retrieved examples has the expected label | Whether the retrieved context contains any same-label example |
| `retrieval_label_matches_at_3` | Integer from 0 to 3 | Count of the first three retrieved examples whose label equals the expected label | How many retrieved examples share the expected label |

The retrieval-label metrics are diagnostics, not direct measures of semantic relevance. Vector search and JEV reranking do not receive the held-out label. A retrieved example can be useful even when its label differs, and a same-label example can still be a weak semantic match.

## MLflow LLM Judges

### Response Quality

| Metric | Per-case scale | Calculation | What it measures |
| --- | --- | --- | --- |
| `correctness` | `yes` or `no` | The judge compares the complete response with `expected_response`. The mean is the proportion judged correct. | Whether the response supports the expected label, confidence, and rationale facts |
| `relevance_to_query` | `yes` or `no` | The judge compares the trace input with the response. The mean is the proportion judged relevant. | Whether the response directly addresses the requested classification |

Correctness and relevance answer different questions. A response can address the classification request and therefore be relevant while still differing from the expected confidence or rationale and therefore fail correctness. Correctness is also broader than `label_exact_match` because it evaluates the complete response rather than only the label.

### Tool Use

| Metric | Per-case scale | Calculation | What it measures |
| --- | --- | --- | --- |
| `tool_call_correctness` | `yes` or `no` | The judge reviews the request, available tools, selected tool, and arguments. The mean is the proportion judged correct. | Whether `record_classification` was a reasonable tool choice with reasonable arguments |
| `tool_call_efficiency` | `yes` or `no` | The judge reviews the tool trajectory for duplicate or unnecessary calls. The mean is the proportion judged efficient. | Whether the classification was recorded without redundant tool use |

No expected tool-call list is supplied, so tool-call correctness uses MLflow's ground-truth-free LLM judgment rather than exact argument matching. The held-out set contains classification tasks only. These scores do not evaluate `get_summary` or `plot_distribution`.

### Dynamic Few-Shot Retrieval

| Metric | Scale | Calculation | What it measures |
| --- | --- | --- | --- |
| `retrieval_relevance` | `yes` or `no` per retrieved example | The judge compares each retrieved example with the request. `/mean` averages all example-level judgments. | Whether each example is semantically useful for the input |
| `retrieval_relevance/precision` | 0 to 1 per trace | Relevant examples divided by all retrieved examples. `/mean` averages the per-trace precision values. | The fraction of supplied context judged relevant |
| `retrieval_groundedness` | `yes` or `no` per trace | The judge compares the complete response with the final retrieved context. The mean is the proportion judged grounded. | Whether response claims are supported by the retrieved examples |

`retrieval_relevance/mean` averages every example-level judgment, while `retrieval_relevance/precision/mean` averages the precision calculated for each trace. They are equal when every trace contains the same number of retrieved examples, but they can differ when retrieval counts vary.

Retrieval precision and groundedness also measure different behavior. Precision asks how much of the retrieved context is useful. Groundedness asks whether that context supports the final response. The system can retrieve three related examples and receive high precision while still failing groundedness when those examples do not support the response's full rationale, confidence, or record-keeping statement.

## MLflow Documentation

- [Built-in LLM judges](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/)
- [LLM judges and scorers](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/)
- [Evaluate stored traces](https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/)
- [`mlflow.genai.evaluate` Python API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate)
- [MLflow tracing](https://mlflow.org/docs/latest/genai/tracing/)
