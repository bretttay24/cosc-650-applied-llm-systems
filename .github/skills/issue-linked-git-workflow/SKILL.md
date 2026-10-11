---
name: issue-linked-git-workflow
description: Drafts and validates research-note pull request descriptions and optional issue-linked engineering workflows for this course repository. Uses weekly findings and developer-authored causal rationale, preserves week-based branches, and links research issues created after the assignment. Saves drafts in the active week's agent-skills-output directory for manual publication. Use when reviewing findings, validating a research issue, naming a course or issue branch, or preparing a pull request.
license: MIT
metadata:
  author: Brett Taylor
  version: "1.5"
---

# Issue-Linked Git Workflow

Use this skill for two related workflows. The default course workflow completes a weekly assignment on a week-based branch, records the results in `findings.md`, creates a GitHub Issue as a research note from those findings, and then drafts the pull request. The existing issue-first engineering workflow remains available when an issue genuinely defines work before implementation begins. Read `AGENTS.md` before applying either workflow because it is the source of truth for current repository conventions.

## Safety

- Draft text and commands by default; do not execute them unless the user explicitly asks.
- Never commit, push, merge, delete a branch, or modify Git history without explicit user approval.
- Do not stage unstaged files unless the user explicitly identifies them for inclusion.
- Never include API keys, `.env` contents, credentials, or other secrets in issues, branches, commits, or pull requests.
- Do not invent an issue number or developer initials. Ask for missing values.
- Save drafts locally only. Do not create or update GitHub Issues or pull requests; the user publishes drafts manually.

## Draft Files

When the user asks for an issue or pull request draft, identify the active course week from the current work or ask which week applies.

- Write issue drafts to `notes/week-<number>/agent-skills-output/issue_draft.md`.
- Write pull request drafts to `notes/week-<number>/agent-skills-output/pr_draft.md`.
- For Week 1, use `notes/week-1/agent-skills-output/issue_draft.md` and `notes/week-1/agent-skills-output/pr_draft.md`.
- Create the output directory or draft file when it does not exist, but do not overwrite unrelated draft content without confirming first.
- After writing a draft, tell the user which file was updated so they can add it to GitHub manually.
- In the course research workflow, `.github/prompts/research-finding-issue.prompt.md` owns creation of `issue_draft.md`; this skill reads and validates that draft when preparing the pull request.

## Weekly Findings

Before drafting a pull request, read `week-<number>/findings.md` for the active week. Use it as the source of truth for the week's observed results and the developer's explanation of what may have caused them.

- If `findings.md` is missing, ask the developer to identify or complete the active week's findings file before continuing.
- Distinguish observations and practical consequences from causal rationale. Measurements, result summaries, and impact statements do not explain why a result occurred.
- Evaluate the substance of the rationale; do not require a specific heading such as `Reasoning` or `Rationale`.
- Do not infer a finished rationale from the notebook, code changes, prior weeks, or course readings.
- Never invent, complete, or silently strengthen the developer's causal explanation.
- Prior-week findings and course material may inform the developer's reasoning, but use them only after the developer identifies the relevant connection.

## Workflow Modes

Choose the workflow from the sequence the developer actually followed. Do not treat a research-note issue created after an assignment as though it authorized the work beforehand.

### Course Research Workflow (Default)

1. Create a week-based branch before beginning the assignment, normally `<developer_initials>_Week<number>`.
2. Complete the weekly notebook, code, evaluation, tests, and supporting documentation on that branch.
3. Create `week-<number>/findings.md` from the completed work. Treat it as the source of truth for measurements and developer-authored causal rationale.
4. Run `/Research-Finding-Issue` from `.github/prompts/research-finding-issue.prompt.md` to create `issue_draft.md` from the notebook and findings. The developer publishes the issue manually as a research note.
5. Use this skill to draft `pr_draft.md` after the research issue exists. Link the verified issue and describe the completed assignment, findings, rationale, implementation, and testing.
6. Use `Refs #<issue-number>` by default because the issue documents the research finding rather than defining work that the pull request resolves. Use `Fixes` only when the developer explicitly says merging should close the issue.
7. Provide push and pull request commands only when explicitly requested. Merge only after review, and leave branch deletion as a manual decision unless explicitly requested.

In this mode, the issue number is not expected to appear in the branch name or in commits created before the research issue existed. Do not rename a week branch or rewrite commit history merely to add a later research-issue number.

### Issue-First Engineering Workflow (Optional)

1. Draft a GitHub Issue in the active week's `issue_draft.md` that provides context, reproduction steps, a proposed direction, and proposed labels. Add acceptance criteria only when the user or repository requires them. The user creates the issue on GitHub manually.
2. Create a branch from the intended base branch using `<developer_initials>_<issue-number>`.
3. Make focused changes, including relevant tests and documentation.
4. Verify that related commits follow the convention below when reviewing issue and pull request linkage.
5. Review the active week's `findings.md`, apply the rationale gate below, and draft the pull request in the active week's `pr_draft.md`. Link it to the issue and describe what changed, what may have caused the findings, why they matter, how the work was implemented, and how the outcome was tested.
6. Provide push and pull request commands only when the user explicitly requests them. The user runs the commands and publishes the pull request manually.
7. Merge only after review. Branch deletion remains a manual decision unless explicitly requested.

## Research Issue Drafting

For the course research workflow, use `.github/prompts/research-finding-issue.prompt.md` after the notebook and `findings.md` are complete. That prompt defines the research-note issue structure and writes the result to the active week's `issue_draft.md`.

Before drafting a pull request, read the published research issue or the local draft and verify that its title, parameters, measurements, and surprise note agree with the notebook and `findings.md`. Do not replace the research-note structure with reproduction steps, proposed solutions, or acceptance criteria unless the developer explicitly requests them.

## Engineering Issue Drafting

For the optional issue-first engineering workflow, write the completed draft to the active week's `notes/week-<number>/agent-skills-output/issue_draft.md`. Use a concise, outcome-focused title. Include enough context that a person or coding agent can understand and reproduce the work without relying on chat history. Propose a practical direction without treating it as final when implementation details still require investigation. Suggest a small set of relevant GitHub labels without assuming those labels already exist.

```markdown
Title: Concise issue title

## Context
Describe the need, source material, constraints, and intended outcome.

## Steps to Reproduce
1. List the inputs and actions needed to observe or investigate the issue.
2. Keep the steps concrete and reproducible.

## Proposed Direction / Solutions
- Describe the likely implementation approach, relevant files or tools, and important tradeoffs.

## Proposed Labels
- `label-name`
```

Example:

```markdown
Title: Set up local Jupyter development

## Context
The course repository needs a reproducible local notebook environment using Python and UV without Google Colab integration.

## Steps to Reproduce
1. Clone the repository.
2. Run `uv sync`.
3. Open a notebook and select the project environment as its kernel.

## Proposed Direction / Solutions
- Declare the supported Python version and notebook dependencies in `pyproject.toml`.
- Use UV to create and synchronize the local environment.
- Store secrets in an ignored `.env` file and provide a safe `.env.example` template.
- Document how to select the project environment as the local Jupyter kernel.

## Proposed Labels
- `documentation`
- `setup`
```

## Branch Naming

### Course Research Branches

Use a week-based branch created before the assignment:

```text
<developer_initials>_Week<number>
```

Examples:

```text
BT_Week6
BT_Week7
```

The later research issue does not need to match the branch name.

### Issue-First Engineering Branches

Use this format:

```text
<developer_initials>_<issue-number>
```

Examples:

```text
BT_2
BT_27
```

The number must match the GitHub Issue for the work. Do not add descriptions or unrelated numbers to the branch name.

Example command:

```powershell
git checkout -b BT_27
```

Before reviewing issue-first engineering work, verify that the current branch number matches the issue being referenced. Do not apply this check to a week-based course research branch.

## Commit Convention (Reference Only)

For the course research workflow, commits may predate the research issue and therefore do not need a reference to that later issue. Do not amend or rewrite those commits solely to add the research issue number. Continue to verify that commit subjects are focused, descriptive, and imperative.

For the issue-first engineering workflow, commits linked by issues and pull requests use this structure:

```text
<Imperative subject without a period>

Refs #<issue-number>
```

The subject is focused and imperative, completing "If applied, this commit will ___." Use this convention only to verify relationships while drafting issues or pull requests. Do not inspect staged changes, draft commit messages, or run `git commit`; the `commit-message` skill owns that workflow.

## Pull Request Drafting

Write the completed draft to the active week's `notes/week-<number>/agent-skills-output/pr_draft.md`. Use an outcome-focused title that reflects the assignment's primary research or engineering outcome. In the course research workflow, the issue documents that outcome; it is not necessarily a work item being resolved.

Frame the title and `What` section around the primary engineering or course objective demonstrated by the work. Treat the experiment's domain scenario as the concrete application of that objective. Do not let one case-specific metric obscure the broader objective when versioning, evaluation, reproducibility, or another engineering practice is itself the subject of the work.

Lead with the issue's outcome rather than routine repository maintenance. Include significant supporting changes for transparency, but keep them secondary unless those artifacts are part of the engineering objective. For example, versioned prompts, shared configuration, saved evaluations, and changelogs are primary outcomes when the work studies prompts as engineering artifacts. Ground results in the active week's `findings.md` and explain both what the measurements mean and the developer's reasoning about why they occurred.

Before drafting, use [the findings-rationale guide](references/findings-rationale.md) to assess whether `findings.md` contains a substantive causal explanation. A sufficient rationale connects an underlying mechanism or concept to specific observed evidence and acknowledges uncertainty, limitations, or plausible contributing factors where appropriate.

If the rationale is absent, merely restates the findings, or makes unsupported causal assertions:

1. Ask the developer focused questions from the guide about relevant current-week readings, prior course concepts, possible mechanisms, supporting evidence, alternative explanations, and limitations.
2. Pause PR drafting until the developer responds or updates `findings.md`.
3. Incorporate only the reasoning the developer provides. Preserve uncertainty and do not answer the reflection questions on the developer's behalf.

When the work compares a baseline with an intervention, preserve the developer's first-person causal reasoning and make the controlled comparison clear: identify the baseline, the isolated change, the variables held constant, the supporting evidence, and the limits of generalization. Correct grammar and improve clarity without replacing the developer's explanation with agent-supplied reasoning.

Use `What`, `Why`, `How`, and `Testing` sections. Add `Related Issue` and `Links` sections when an issue and publication artifacts are available:

- In `Related Issue`, provide a visible Markdown link containing the issue number and title. Verify the issue exists; do not invent its title or URL.
- At the end of the draft, use `Refs #<issue-number>` for a course research-note issue unless the developer explicitly requests closure. Use `Fixes #<issue-number>` only when merging should close an issue.
- In `Links`, list each developer-requested artifact as its own Markdown link. Do not bury these links inside descriptive `How` bullets.
- When the branch is already pushed to GitHub, link artifacts to that branch so newly added files resolve before merge. Verify the repository, branch, path, and filename before drafting the URL.
- Keep `How` focused on the implementation and analysis workflow even when the same artifacts appear in `Links`.

Testing should report behavior-oriented evidence relevant to the issue, such as tests that pass, notebook execution, or manual output verification. Do not include internal checks performed only to draft or validate the pull request, such as branch inspection, secret scans, commit-format review, or diff whitespace checks, unless they reveal a limitation that affects the change.

```markdown
Title: Concise outcome-focused title

## What
Summarize the primary engineering or course objective, the domain scenario used to demonstrate it, and headline findings from the active week's `findings.md`.

## Why
Explain why the result matters and present the developer's reasoning about its underlying cause. Connect the proposed mechanism to observed evidence and relevant current or prior course concepts or readings. State uncertainty, limitations, and plausible contributing factors where appropriate.

## How
Describe the relevant inputs, controlled changes, implementation artifacts, and analysis method.

## Testing
- List behavior-focused tests, notebook runs, or manual verification.
- Note limitations that affect confidence in the result.

## Related Issue
- [#<issue-number>: Verified issue title](https://github.com/<owner>/<repo>/issues/<issue-number>)

## Links
- [Named artifact](https://github.com/<owner>/<repo>/blob/<pushed-branch>/<path>)

Refs #<issue-number>
```

Use `Refs #27` for a research-note issue. Use `Fixes #27` only when merging the pull request should close issue 27.

## Consistency Checks

Before returning a draft, confirm:

- The selected workflow mode matches the actual sequence of work.
- For course research work, the branch follows the established week-based convention and is not required to contain the later issue number.
- For issue-first engineering work, the branch is named `<developer_initials>_<issue-number>` and the branch, commit, and pull request references agree.
- Commit subjects are focused and imperative; do not require a later research issue reference in earlier course commits.
- For an issue-first engineering issue, the issue provides sufficient context, reproducible steps, a practical direction, and relevant proposed labels.
- For a course research issue, the issue follows `research-finding-issue.prompt.md` and agrees with the notebook and `findings.md`.
- The pull request's findings agree with the active week's `findings.md`.
- The title and `What` section foreground the primary engineering or course objective, with the domain scenario presented as its application when appropriate.
- The `Why` section contains the developer's causal reasoning, not only repeated findings, impacts, or an agent-supplied explanation.
- The rationale connects a possible mechanism to evidence and preserves relevant uncertainty, alternatives, and limitations.
- A controlled comparison identifies the baseline, isolated intervention, constants, supporting evidence, and limits when those elements apply.
- The `Related Issue` section visibly links the verified issue, and the closing keyword matches whether the PR should resolve it.
- Each developer-requested artifact appears as a separate entry in `Links`, and pushed-branch URLs use verified repository paths.
- The proposed commit includes only staged changes.
- No secret or `.env` value appears in generated text.