---
name: issue-linked-git-workflow
description: Drafts and validates GitHub Issues, issue-linked branch names, and pull request descriptions for this repository. Saves drafts in the active week's agent-skills-output directory for manual publication. Use when creating an issue, naming a branch, verifying issue and commit linkage, or preparing a pull request.
license: MIT
metadata:
  author: Brett Taylor
  version: "1.2"
---

# Issue-Linked Git Workflow

Use this skill to keep GitHub Issues, branches, commit references, and pull requests connected throughout a change. Read `AGENTS.md` before applying the workflow because it is the source of truth for current repository conventions.

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

## Workflow

1. Draft a GitHub Issue in the active week's `issue_draft.md` that provides context, reproduction steps, a proposed direction, and proposed labels. Add acceptance criteria only when the user or repository requires them. The user creates the issue on GitHub manually.
2. Create a branch from the intended base branch using `<developer_initials>_<issue-number>`.
3. Make focused changes, including relevant tests and documentation.
4. Verify that related commits follow the convention below when reviewing issue and pull request linkage.
5. Push the branch and open a pull request only when the user explicitly requests those actions.
6. Draft the pull request in the active week's `pr_draft.md`, linking it to the issue and describing what changed, why it matters, how it was implemented, and how the outcome was tested. The user creates the pull request on GitHub manually.
7. Merge only after review. Branch deletion remains a manual decision unless explicitly requested.

## Issue Drafting

Write the completed draft to the active week's `notes/week-<number>/agent-skills-output/issue_draft.md`. Use a concise, outcome-focused title. Include enough context that a person or coding agent can understand and reproduce the work without relying on chat history. Propose a practical direction without treating it as final when implementation details still require investigation. Suggest a small set of relevant GitHub labels without assuming those labels already exist.

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

Before reviewing linked work, verify that the current branch number matches the issue being referenced.

## Commit Convention (Reference Only)

Commits linked by issues and pull requests use this structure:

```text
<Imperative subject without a period>

Refs #<issue-number>
```

The subject is focused and imperative, completing "If applied, this commit will ___." Use this convention only to verify relationships while drafting issues or pull requests. Do not inspect staged changes, draft commit messages, or run `git commit`; the `commit-message` skill owns that workflow.

## Pull Request Drafting

Write the completed draft to the active week's `notes/week-<number>/agent-skills-output/pr_draft.md`. Use an outcome-focused title that reflects the issue being resolved.

Lead with the issue's outcome rather than repository maintenance or supporting infrastructure. Include significant supporting changes for transparency, but keep them secondary unless they are the subject of the issue. Ground results in the actual source material or inputs and explain what the measurements mean, not just the resulting numbers.

Use `What`, `Why`, `How`, and `Testing` sections. Testing should report behavior-oriented evidence relevant to the issue, such as tests that pass, notebook execution, or manual output verification. Do not include internal checks performed only to draft or validate the pull request, such as branch inspection, secret scans, commit-format review, or diff whitespace checks, unless they reveal a limitation that affects the change.

```markdown
Title: Concise outcome-focused title

## What
Summarize the issue outcome and its key results.

## Why
Explain the problem, why it matters, and the result's practical meaning.

## How
Describe the relevant inputs or sources and the implementation or analysis method. Link source material when appropriate.

## Testing
- List behavior-focused tests, notebook runs, or manual verification.
- Note limitations that affect confidence in the result.

Fixes #27
```

Use `Fixes #27` only when merging the pull request should close issue 27. Use `Refs #27` when the pull request relates to the issue but does not fully resolve it.

## Consistency Checks

Before returning a draft, confirm:

- The branch is named `<developer_initials>_<issue-number>`.
- The branch issue number, commit reference, and pull request reference agree.
- The commit subject is imperative and passes the sentence test.
- The issue provides sufficient context, reproducible steps, a practical direction, and relevant proposed labels.
- The proposed commit includes only staged changes.
- No secret or `.env` value appears in generated text.