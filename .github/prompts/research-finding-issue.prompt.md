---
name: "Research Finding Issue"
description: Draft a GitHub issue from a research notebook and findings file with exact parameters, results, and a short personal surprise note.
argument-hint: "Notebook path and findings path"
agent: "agent"
model: "GPT-5.6 Sol"
---

Create a publication-ready GitHub issue that documents a research finding from the notebook and findings files named by the user.

Follow these requirements:

- Read the source notebook and findings file before drafting.
- Ground every parameter and measurement in those files. Do not invent, estimate, or silently correct results.
- Use a clear, concise, outcome-focused title.
- Include the exact model, prompt, random seed, and inference or sampling parameters used. Preserve numeric precision when it matters.
- Summarize the important findings with measured values.
- Include a short first-person note explaining what surprised the researcher. Preserve their stated perspective and uncertainty rather than inventing a reaction.
- Mention a verified implementation artifact only when it materially affects interpretation of the findings.
- Suggest a small set of relevant labels without assuming those labels exist.
- Do not add steps to reproduce, proposed solutions, acceptance criteria, or other issue-workflow sections unless the user explicitly requests them.
- Do not publish the issue. Save the draft to `notes/week-<number>/agent-skills-output/issue_draft.md`, where `<number>` is inferred from the source paths. If that file already exists, read it first and preserve intentional user edits.

Use exactly this output structure:

```markdown
Title: Clear research finding title

## Context

Briefly identify the experiment, source files, and research question.

## Exact Parameters Used

- `parameter=value`

## Results and Surprise

- Report the key measured findings.

What surprised me most was ...

## Proposed Labels

- `research`
```

After saving the draft, validate that the title is clear, all stated parameters are exact, the findings match the sources, and the surprise note is brief and grounded in the researcher's own observations. Report the saved file path to the user.