# Week 4 Research Note: Multi-Tool Assistant

## Scope

This note summarizes `week4_tool_use.ipynb`, which extends the Week 3 HCAHPS classifier into a multi-tool assistant. The assistant uses an LLM to interpret patient comments and deterministic tools to record classifications, summarize the ledger, calculate focused statistics, and plot label distributions.

The experiment examined a multi-step ordering failure. One request asked the assistant to classify a new comment and then report the percentage of high-confidence predictions. The correct result required `record_classification` to run before `run_guarded_summary_statistic` so the percentage included the new record.

## Exact Configuration

- Model: `gpt-4o`
- Prompt: `hcahps-classifier`
- Baseline system prompt: `v1`
- Revised system prompt: `v2`
- Temperature: `0.2`
- Maximum output tokens: `450`
- Maximum agent iterations: `4`
- Random seed: not set
- Tools: `record_classification`, `get_summary`, `plot_distribution`, and `run_guarded_summary_statistic`
- Guarded-statistics record limit: `50`
- Guarded-statistics elapsed-time budget: `0.25` seconds

No random seed was configured for the model calls, so repeated requests could produce different tool-call sequences.

## Failure Case

With the original guarded-statistics tool description and system prompt `v1`, the ordering failure occurred approximately 50% of the time during manual runs. The model called `run_guarded_summary_statistic` before `record_classification`, so the returned percentage excluded the new comment. After recording the comment on the next turn, the final response omitted the percentage requested by the user.

The first intervention changed only the guarded-statistics tool description. It explicitly stated that every patient comment in the request must be recorded before the statistic is calculated. Three of the four initial runs followed the intended sequence, for a 75% observed success rate. The remaining run still calculated the statistic first. Three additional reruns did not reproduce the error, but that did not establish that the description alone reliably enforced the sequence.

The second intervention retained the revised tool description and changed the system prompt from `v1` to `v2`. The new prompt explicitly directed the model to classify and record a supplied comment before calculating a requested statistic. All four saved runs then called `record_classification` before `run_guarded_summary_statistic` and returned the high-confidence percentage.

Repeated attempts reused comment ID `19`. After the first successful classification, `record_classification` returned a structured duplicate-ID error, but the model continued to the statistics call and final answer. This demonstrated error handling, although it was separate from the tool-ordering question.

## Guarded Statistics Design

The statistics tool accepts four read-only operations: `total_classifications`, `most_common_label`, `percentage_for_label`, and `percentage_for_confidence`. It does not accept Python source code. Its schema and dispatcher block arbitrary code, imports, filesystem access, network access, process execution, ledger modification, and unsupported statistics. A 50-record limit and 0.25-second elapsed-time budget bound the work.

## Conclusion

Clarifying the tool description improved the tool call order but did not consistently correct it in the initial four runs. Adding  guidance to the system prompt, while retaining the revised tool description, produced the intended order in all four saved runs.

What surprised me most was that describing what the guarded-statistics tool does was not enough to reliably control when the model called it. The model appeared to need explicit guidance about the dependency between recording the new classification and calculating the updated percentage.

This was a small, non-deterministic manual evaluation. Because the second intervention retained the revised tool description, the experiment did not isolate the effect of system prompt `v2` by itself. The results therefore show a successful combined intervention for this failure.