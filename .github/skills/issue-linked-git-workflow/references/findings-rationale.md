# Findings Rationale Guide

Use this guide only when reviewing the active week's `findings.md` before drafting a pull request. Its purpose is to help the developer reason about the findings, not to supply that reasoning for them.

## Distinguish the Parts

- **Finding:** What was observed or measured.
- **Impact:** Why the observation matters in practice.
- **Rationale:** What underlying mechanism could have produced the observation and why the available evidence supports that explanation.

Repeating a measurement in different words or describing its cost, capacity, quality, or performance consequence is not a causal rationale.

## Rationale Check

Treat the rationale as substantive when the developer has addressed the relevant parts below:

- Names a possible mechanism, theory, or course concept.
- Connects that mechanism to specific evidence in the findings, notebook, experiment, or implementation.
- Relates the explanation to this week's readings or concepts, or to relevant material from a previous week.
- Distinguishes evidence from inference and uses appropriately tentative language when the cause was not directly tested.
- Considers plausible contributing factors, alternative explanations, confounders, or limitations.

Do not require every item when it does not apply. Do require more than a restatement or an unsupported claim that one factor caused the result.

## Reflection Questions

When rationale is missing or weak, select a small number of questions that best fit the findings and ask the developer:

1. What did you read this week that could explain why this result occurred?
2. What concept or finding from a previous week in the course may also apply?
3. What underlying mechanism would produce the pattern you observed?
4. Which specific result or example supports that mechanism?
5. Did the experiment test the proposed cause directly, or is it a hypothesis?
6. What other factors could have contributed to the result?
7. What evidence would weaken or disprove your explanation?
8. What limitation should a reader consider before generalizing the finding?

Pause after asking. Do not answer these questions, search for an explanation to insert, or rewrite a weak claim into a stronger one on the developer's behalf.

## BPE Teaching Example

For a tokenization finding, stating that Spanish used more tokens than English only repeats the result. Stating that this increases cost or reduces context capacity explains the impact, not the cause.

A developer might investigate whether frequency-based byte-pair encoding merges, representation of each language in vocabulary construction data, tokenizer vocabulary size, or distinct Unicode punctuation sequences could explain observed token splits. These possibilities become rationale only when the developer:

- selects and explains the relevant mechanism;
- connects it to observed token pieces or tokenizer comparisons;
- identifies a course reading, source, or concept that supports the explanation; and
- separates supported conclusions from hypotheses and other contributing factors.

Use this example to prompt analysis. Do not assume BPE is the cause of every tokenization disparity, attribute training-data composition without support, or place this explanation into the pull request unless the developer supplies it.