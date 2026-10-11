# Week 7 Research Note: The Adaptation Decision and Dynamic Few-Shot

## Scope

This note summarizes `week7_adaptation.ipynb`, which asks whether fine-tuning is justified for a task before committing to it. The task is answering developer questions about the Microsoft Agent Framework Python API, including documented defaults, return types, and exceptions. The assignment covers Part 1 (prepare a synthetic dataset), Part 2 (adapt with dynamic few-shot prompting), Part 3 (evaluate against a zero-shot baseline and show a failure), and Part 4 (an adaptation decision memo).

Dynamic few-shot was the cheapest adaptation I could test before fine-tuning: for each held-out question, retrieve the most similar training samples and place them in the prompt. If giving the model training samples with ground-truth answers does not help enough, that is evidence about what a fine-tuned model could realistically add. The comparison is scored by an LLM judge because the data are open-ended question and answer pairs, not labeled classification data.

## Exact Configuration

- Source: Microsoft Agent Framework Python API reference PDF (2,423 pages), split into three PDF parts
- Data generation: Microsoft Foundry, supervised fine-tuning, Simple Q&A (single turn), Short answer, GPT-5.4 generator, max 150 samples per part
- Dataset: 361 records, merged from the Foundry training and validation files
- Splits: 311 training, 50 held-out evaluation, stratified by question length
- Token lengths (system + user + assistant content, tiktoken o200k_base): range 38 to 414, median 118, mean 137.2
- Retrieval index: training questions only, embedded with `all-MiniLM-L6-v2` in the local pgvector store, one chunk per training sample
- Retrieval: `retrieval_k=10`, `pool_k=10`, Jev reranking enabled, `final_k=3`
- Generation model: `gpt-5.6-luna` for both zero-shot and dynamic few-shot, with identical instructions
- Judge: blind LLM judge through Foundry, scoring API identification (0-2), purpose accuracy (0-2), and usage guidance (0-1), total 0-5
- Held-out reference answers are shown only to the judge, never to the generation prompt
- Evaluation: 50 questions, 2 approaches, 100 generated answers and 100 judge calls

## Findings: Dataset Preparation

The Foundry data required no cleaning by the notebook's checks. All 361 records parsed, with no blank or malformed lines, filtered records, duplicate question-answer pairs, or invalid formats. Training and evaluation token-length distributions were similar: medians of 118 and 128, and 90th percentiles of 239 and 234.

Those checks only test format, not answer quality. 

## Findings: Zero-Shot vs. Dynamic Few-Shot

| Approach | API identification | Purpose accuracy | Usage guidance | Mean total |
|---|---:|---:|---:|---:|
| Zero-shot | 1.82 | 1.56 | 0.68 | 4.06 |
| Dynamic few-shot | 1.96 | 1.80 | 0.80 | 4.56 |

**Aggregate quality.** Dynamic few-shot improved the mean total by 0.50 points on the 5-point rubric. The largest component gain was purpose accuracy (+0.24), followed by API identification (+0.14) and usage guidance (+0.12). Zero-shot already scored 4.06 out of 5, so the model has useful baseline knowledge of the framework and the headroom was limited.

**Where few-shot hurt.** Dynamic few-shot scored below zero-shot on 9 of 50 questions (18%). Two of those dropped by 2 points (`dapr_secret_input` and `Executor.is_request_supported`, both 5 to 3), and seven dropped by 1 point. 


## Failure Case

Held-out evaluation 5 asks: **"What does `Edge.to_dict` include when the edge's `condition_name` is known?"** The reference answer is that it includes the source and target executor identifiers plus the condition name. Zero-shot scored 4/5. It included source, target, and condition, but the judge noted that it did not clearly present source and target as executor identifiers and added field-level details the reference does not establish. Dynamic few-shot scored 3/5. It stated that the condition name is included and that the live callable is omitted, but it left out the source and target identifiers entirely, and the judge flagged the callable claim as unsupported by the reference.

The three retrieved examples were all about `Edge` serialization, and none stated the missing fact: reconstruction with `from_dict` and the preserved `condition_name` (JEV 0.710), why `to_dict` omits the live callable (0.530), and how `to_json` relates to `to_dict` (0.190). The model reflected what the examples emphasized, which was that the callable is omitted, instead of what the question asked. The retrieval was on topic but not on the specific fact, and the examples gave the model something plausible to repeat in place of the answer. 

The selected case is a 1-point drop, not the worst one. I picked it because the retrieved examples make the mechanism visible. It also showed up with each rerun of the notebook. The non determinism of the generated outputs and the judge make it difficult to get the same failure cases. This one was constant across runs. 

## Adaptation Decision

The memo recommends a concise task prompt plus source-grounded RAG over the full API reference, and not fine-tuning now.

- **Prompting:** necessary as the interface, but zero-shot alone (4.06/5) is not reliable enough for exact developer documentation answers.
- **RAG:** the experiment retrieves Q&A examples from the training split, not source documentation, so it shows the value of retrieval-assisted prompting without measuring a production RAG system. The next step is retrieval over the API reference with citations, tested on this same 50-question set.
- **Dynamic few-shot:** keep it as a baseline or supplement. Its examples come from the same synthetic dataset and can be adjacent instead of authoritative, as the `Edge.to_dict` case shows.
- **Fine-tuning:** the main gap is factual and changing API knowledge, which is easier to refresh and audit through retrieval than in model weights. Fine-tuning becomes reasonable only after a strong RAG baseline still shows repeated behavioral failures in format, tone, or reasoning.
- **Doing nothing:** not justified. The 0.50-point gain and the need for exact API details leave room for improvement.

## Conclusion

Dynamic few-shot raised the mean judged score from 4.06 to 4.56 without training a model, mostly through better purpose accuracy and API identification. It also made 9 of 50 answers worse, and the failure inspected shows retrieval that is related to the question but missing the needed fact. That pattern points toward grounding answers in source documentation, and away from fine-tuning, as the next step.

