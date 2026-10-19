# Week 8 Capstone Findings: HCAHPS-Aligned Patient Feedback Agent

## Scope

These findings summarize `capstone_llm_system.ipynb`, which integrates techniques from Weeks 3 through 7 into one patient-feedback classification system. The agent maps supplemental free-text patient comments to one primary HCAHPS-aligned theme, records the classification in a session-owned ledger, and can summarize or visualize the comments processed during that session.

The system does not administer the official HCAHPS survey or calculate HCAHPS scores. Its labels, counts, and percentages describe synthetic narrative comments organized under HCAHPS-aligned themes.

The capstone has three parts. Part 1 integrates the earlier course components. Part 2 evaluates the complete agent on 20 held-out comments. Part 3 examines one trace where the label was correct but the confidence did not match the expected result.

## Exact Configuration

- Agent framework: Microsoft Agent Framework
- Generation model for agent: `gpt-5.6-luna`
- Prompting: version-controlled classifier instructions and model configuration from Week 3
- Tools: Pydantic-validated recording, summary, and visualization tools adapted from Week 4
- Retrieval: `text-embedding-3-small` with PostgreSQL and pgvector cosine-distance search
- Retrieval pool: five semantically similar training comments
- Reranking: JEV probability of relevance
- Final dynamic context: three complete labeled examples
- Classification gate: Decision-1 with a `0.5` threshold
- Evaluation set: 20 held-out synthetic patient comments, each run in a fresh agent session
- Deterministic evaluation: exact label match, exact confidence match, retrieval label hit at 3, and matching retrieval labels at 3
- LLM judges: MLflow correctness, query relevance, tool-call correctness, tool-call efficiency, retrieval relevance, and retrieval groundedness, with gpt-5-mini
- Observability: MLflow traces containing the chain, retrieval, model, and tool spans

## Findings: Integrated System

The final system keeps language interpretation separate from deterministic state changes. The model selects a label, confidence, and rationale, while the recording tool validates the schema and stores the result. Summary and visualization tools calculate their outputs from the session ledger rather than asking the model to reconstruct prior classifications from conversation history.

Dynamic prompting runs only for classification requests. Decision-1 allows summary and visualization requests to bypass retrieval. For a classification request, the middleware embeds the patient comment, retrieves five candidates from pgvector, reranks them with JEV, and inserts the top three complete examples into the final user message. This design reuses the Week 7 dynamic few-shot approach while adding a gate for an agent that supports more than one task.

MLflow tracing made the complete execution path inspectable. Each held-out classification could be connected to its retrieved examples, model response, validated tool call, deterministic result, and LLM-judge rationale. The stored traces were evaluated after classification, so the candidate agent did not have to run again for each judge.

## Findings: Evaluation

| Evaluation | Mean |
| --- | ---: |
| Label exact match | 1.00 |
| Confidence exact match | 0.95 |
| Retrieval label hit at 3 | 1.00 |
| Matching retrieval labels at 3 | 2.45 of 3 |
| Response correctness | 0.95 |
| Relevance to query | 1.00 |
| Tool-call correctness | 1.00 |
| Tool-call efficiency | 1.00 |
| Retrieval relevance | 0.967 |
| Retrieval relevance precision | 0.967 |
| Retrieval groundedness | 0.55 |

The deterministic results show that the classifier selected the expected HCAHPS-aligned theme for all 20 held-out comments. Confidence matched the synthetic expectation for 19 of 20 comments. The expected label appeared in the top three retrieved examples for every case, with an average of 2.45 matching labels among the three examples.

The LLM judges supported the same overall pattern. Every response addressed the classification request, and the tool judges found the recorded calls correct and efficient. Response correctness was lower than deterministic label accuracy because the judge compares the complete response, including confidence and rationale, rather than the label alone.

Retrieval relevance was high, but retrieval groundedness was lower. This distinction matters. Relevance asks whether the examples are useful for the request, while groundedness asks whether those examples support the complete response. An example can be related to a patient comment without directly supporting every detail in the generated rationale or the selected confidence level.

## Failure Case

The selected failure was the user comment:

> "unfamiliar patch appeared on my arm and idk who put it there or what it was for"

The expected and predicted labels were both `communication_medicines`. The expected confidence was `high`, but the agent recorded `medium`. The rationale still identified the central issue: an unfamiliar treatment or medication was applied without an explanation.

The retrieved context may help explain the confidence disagreement. The highest-ranked example concerned changing a dressing and was labeled `discharge_information`. The other two examples concerned unexplained medicines and were labeled `communication_medicines`. The word `patch` can describe either a medication patch or a wound dressing. JEV appears to have favored the semantic relationship between `patch` and `dressing`, even though that example represented a different patient-experience theme.

The agent therefore received mixed evidence. Two examples supported medicine communication, while the first example supported discharge information. The final label was correct, but uncertainty about the treatment type likely caused the model to lower its confidence.

The groundedness judges also exposed a limitation in the evaluation. One judge treated the recorded `medium` confidence as evidence against the expected `high` response. The retrieval-groundedness judge recognized that the medicine examples were similar, but it also expected the retrieved examples to support trace-level claims about the specific comment being recorded. That requirement goes beyond whether the examples support the classification itself.

## Mitigation

I would add contrastive training examples that clearly distinguish medication patches from wound dressings. Medication-patch examples should emphasize an unexplained medicine or treatment during the stay. Dressing examples should emphasize wound care, discharge instructions, or warning signs.

I would also make the JEV question specific to the classification task. A candidate should be considered relevant when it represents the same patient-experience issue and provides a useful classification example. Shared clinical vocabulary should not be enough when the candidate belongs to a different HCAHPS-aligned theme.

The classifier prompt also needs a clearer confidence policy. The agent should use `high` confidence when the patient-experience theme is clear even if the exact treatment type is uncertain. It should use `medium` when the ambiguity could reasonably change the selected theme.

Finally, the LLM judges would benefit from use-case-specific grading rubrics. 

## Conclusion

The integrated agent classified all 20 held-out comments under the expected HCAHPS-aligned theme. The LLM judges rated all observed tool calls as correct and efficient. Dynamic few-shot retrieval consistently placed at least one example with the expected label in the top three, although related examples did not always provide complete grounding for the response.

The failure case showed why aggregate accuracy is not enough. The correct label hid a retrieval ambiguity, a confidence-calibration disagreement, and a judge rubric that did not fully match the intended use case. MLflow tracing made those differences visible by connecting the aggregate evaluation results to the exact retrieved context, tool call, response, and judge explanations. The most useful next improvements are contrastive examples, classification-specific reranking, clearer confidence guidance, and judge rubrics tailored to the system's HCAHPS-aligned classification task.
