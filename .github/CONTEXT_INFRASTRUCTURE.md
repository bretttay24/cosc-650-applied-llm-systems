# GitHub Context Infrastructure

The `.github/` directory contains version-controlled context and workflow customizations used while completing the course. They are part of the repository's applied LLM systems work: instead of supplying every expectation in an ad hoc chat prompt, the repository makes important context repeatable, task-aware, reviewable, and available to other coding-agent sessions.

These files do not replace critical review of model output. They provide a documented starting point for how an assistant should understand the project, interact with notebooks, and support recurring development tasks.

## Current Layers

| Primitive | Role | Repository implementation | Activation | Why it is used |
|---|---|---|---|---|
| Agent instructions | Shared project structure and conventions for coding agents | [`../AGENTS.md`](../AGENTS.md) | Loaded as repository-level context | Keeps environment, workflow, and safety conventions in one cross-agent source of truth |
| Copilot instructions | GitHub Copilot's repository-wide instruction entry point | [`copilot-instructions.md`](copilot-instructions.md) | Applied to Copilot requests in this repository | Directs Copilot to `AGENTS.md` without maintaining duplicate guidance |
| Path-specific instructions | Rules that apply to matching files or tasks | [`instructions/local-jupyter.instructions.md`](instructions/local-jupyter.instructions.md) | Its `applyTo` pattern matches `week-*/*.ipynb` | Constrains notebook work to local Jupyter and UV while protecting secrets and reproducibility |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/commit-message/SKILL.md`](skills/commit-message/SKILL.md) | Selected when a request matches its description | Drafts a focused commit message from staged changes and adds an issue reference only when requested |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/issue-linked-git-workflow/SKILL.md`](skills/issue-linked-git-workflow/SKILL.md) | Selected when a request matches its description | Drafts research-note pull requests for week-based course branches while retaining an optional issue-first engineering workflow |
| Prompt file | A focused reusable task invoked manually in VS Code Copilot Chat | [`prompts/research-finding-issue.prompt.md`](prompts/research-finding-issue.prompt.md) | Invoked with the source notebook and findings file paths | Produces a source-grounded research issue draft with exact parameters, measured results, and the researcher's stated surprise |

## How the Layers Work Together

When an assistant works on a weekly notebook, `AGENTS.md` supplies the repository-wide conventions and `copilot-instructions.md` provides the Copilot-specific entry point. Because the target matches `week-*/*.ipynb`, the local Jupyter instructions add notebook-specific constraints such as using the UV-managed environment, keeping credentials out of source and output, and executing the notebook from top to bottom.

The workflow customizations are used only when the task calls for them. Preparing a commit message loads the staged-change rules in the `commit-message` skill; an issue reference is optional because weekly course commits often predate the research issue. After an assignment is complete, `week-<number>/findings.md` records the results and developer-authored rationale. The explicitly invoked `research-finding-issue` prompt then reads the notebook and findings file and saves a validated research issue draft under `notes/week-<number>/agent-skills-output/` without publishing it. After the developer publishes that research note, the `issue-linked-git-workflow` skill drafts the pull request, links the verified issue with `Refs`, and preserves the established week-based branch. Its bundled [`findings-rationale.md`](skills/issue-linked-git-workflow/references/findings-rationale.md) guide prevents the PR from substituting agent-generated explanations for the developer's reasoning.

The broader skill also retains an optional issue-first engineering mode for work that genuinely begins with an issue and uses an issue-numbered branch. Keeping both procedures out of always-on instructions avoids adding task-specific context to unrelated notebook work.

## Research-Finding Prompt

The research-finding prompt originated as a Week 2 prompt experiment and is now the recurring post-assignment issue-drafting workflow. It is implemented as [`prompts/research-finding-issue.prompt.md`](prompts/research-finding-issue.prompt.md), using a prompt file as the right primitive for a focused task with parameterized inputs rather than duplicating either multi-step workflow skill.

The prompt requires the user to identify a notebook and findings file. It then:

- Reads both sources before drafting and preserves their reported values without invention, estimation, or silent correction.
- Uses a fixed issue structure covering context, exact parameters, measured results, the researcher's first-person surprise, and proposed labels.
- Includes implementation artifacts only when they materially affect interpretation and omits broader issue-workflow sections unless requested.
- Preserves intentional edits in an existing draft, validates the completed content against the sources, and saves it locally without publishing the issue.

This division keeps the prompt centered on one repeatable research-writing task. The commit skill owns staged-change message drafting, while the broader workflow skill owns research-note PR drafting and the optional issue-first engineering path.

## Design Principles

- Keep repository-wide guidance concise and place specialized rules at the narrowest useful scope.
- Store durable project context in version control so changes can be reviewed with the work they affect.
- Avoid duplicating instructions across files; link to the source of truth instead.
- Describe current behavior in the present tense and experiments in the future tense.
- Treat generated output as material to validate, not as an authoritative result.

## Official References

- [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Use prompt files in VS Code](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [Use agent skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)