# Week 3 Research Note: Prompt Engineering

## Scope

This note summarizes `week3_prompt_engineering.ipynb`, which evaluates two version-controlled prompts for classifying free-text HCAHPS patient-experience comments. The classifier returns a primary label, rationale, and confidence level.

The evaluation uses 20 test cases and measures label accuracy, confidence accuracy, rationale semantic similarity, and token usage. Both prompts used `gpt-4o` with a temperature of `0.2`.

## Prompt Comparison

| Metric | V1 | V2 | Finding |
|---|---:|---:|---|
| Label accuracy | 90% | 100% | V2 corrected both label errors from V1. |
| Confidence accuracy | 80% | 80% | Confidence calibration did not improve. |
| Average rationale semantic similarity | 0.670 | 0.667 | Essentially unchanged; the difference was only 0.003. |
| Average input tokens | 1,089.85 | 1,173.85 | V2 required 84 more input tokens per case. |
| Average output tokens | 40.55 | 38.80 | V2 produced slightly shorter responses. |

V2 added targeted edge-case rules without changing the core label definitions. The new rules clarified that medication explanations during a hospital stay belong to `communication_medicines`, medication understanding after discharge belongs to `care_transition`, and discharge plans that ignore a patient's home situation or abilities belong to `care_transition`.

The V1 prompt misclassified two ambiguous cases. It classified a new shot that was not explained as `communication_nurses` rather than `communication_medicines`, and it classified a discharge plan that ignored the patient's ability to climb stairs as `discharge_information` rather than `care_transition`. V2 classified both cases correctly.

## Failure Case

This prompt experiment showed no regressions on individual test cases. The targeted edge-case guidance improved label accuracy from 90% to 100% without meaningfully changing rationale semantic similarity, which decreased only from 0.670 for V1 to 0.667 for V2. Input token usage increased by fewer than 100 tokens. The prompt remained stable because the revision clarified specific ambiguous cases rather than changing the core label definitions or instructions.

However, the confidence label needs further improvement. The model predicted "high" confidence for every test case, including cases with incorrect labels or confidence values. This pattern limits the usefulness of the confidence field and is a shortcoming shared by both prompt versions.

The remaining failure was confidence calibration. Both V1 and V2 predicted `high` confidence for every test case. As a result, each prompt missed the four cases whose expected confidence was `medium` or `low`, resulting in 80% confidence accuracy.

This is a limitation because a confidence field is only useful when it distinguishes clear cases from ambiguous ones. In this evaluation, the model was highly confident even for cases that required a more cautious prediction.

## Conclusion

Adding targeted edge-case rules improved label accuracy from 90% to 100% without meaningfully changing rationale semantic similarity. The primary tradeoff was an increase of 84 average input tokens per test case, which was acceptable for the improvement in classification accuracy. However, confidence calibration remained a shared weakness in both prompt versions and should be the focus of a future revision.