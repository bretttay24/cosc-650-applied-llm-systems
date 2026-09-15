# GitHub Context Infrastructure

The `.github/` directory contains version-controlled context and workflow customizations used while completing the course. They are part of the repository's applied LLM systems work: instead of supplying every expectation in an ad hoc chat prompt, the repository makes important context repeatable, task-aware, reviewable, and available to other coding-agent sessions.

These files do not replace critical review of model output. They provide a documented starting point for how an assistant should understand the project, interact with notebooks, and support recurring development tasks.

## Current Layers

| Primitive | Role | Repository implementation | Activation | Why it is used |
|---|---|---|---|---|
| Agent instructions | Shared project structure and conventions for coding agents | [`../AGENTS.md`](../AGENTS.md) | Loaded as repository-level context | Keeps environment, workflow, and safety conventions in one cross-agent source of truth |
| Copilot instructions | GitHub Copilot's repository-wide instruction entry point | [`copilot-instructions.md`](copilot-instructions.md) | Applied to Copilot requests in this repository | Directs Copilot to `AGENTS.md` without maintaining duplicate guidance |
| Path-specific instructions | Rules that apply to matching files or tasks | [`instructions/local-jupyter.instructions.md`](instructions/local-jupyter.instructions.md) | Its `applyTo` pattern matches `week-*/*.ipynb` | Constrains notebook work to local Jupyter and UV while protecting secrets and reproducibility |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/commit-message/SKILL.md`](skills/commit-message/SKILL.md) | Selected when a request matches its description | Drafts an issue-linked commit message from staged changes without taking unrelated Git actions |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/issue-linked-git-workflow/SKILL.md`](skills/issue-linked-git-workflow/SKILL.md) | Selected when a request matches its description | Connects issue, branch, commit, and pull request conventions while keeping publication manual |
| Prompt file | A focused reusable task invoked manually in VS Code Copilot Chat | [`prompts/research-finding-issue.prompt.md`](prompts/research-finding-issue.prompt.md) | Invoked with the source notebook and findings file paths | Produces a source-grounded research issue draft with exact parameters, measured results, and the researcher's stated surprise |

## How the Layers Work Together

When an assistant works on a weekly notebook, `AGENTS.md` supplies the repository-wide conventions and `copilot-instructions.md` provides the Copilot-specific entry point. Because the target matches `week-*/*.ipynb`, the local Jupyter instructions add notebook-specific constraints such as using the UV-managed environment, keeping credentials out of source and output, and executing the notebook from top to bottom.

The workflow skills are used only when the task calls for them. For example, preparing a commit message loads the staged-change rules in the `commit-message` skill, while drafting or validating an issue-linked workflow uses the broader `issue-linked-git-workflow` skill. The `research-finding-issue` prompt handles a narrower, explicitly invoked task: it reads a named research notebook and findings file, then saves a validated issue draft under the corresponding `notes/week-<number>/agent-skills-output/` directory without publishing it. Keeping these procedures out of always-on instructions avoids adding task-specific context to unrelated notebook work.

## Week 2 Research-Finding Prompt

The Week 2 prompt experiment is implemented as [`prompts/research-finding-issue.prompt.md`](prompts/research-finding-issue.prompt.md). It tests a prompt file as the right primitive for a focused task with parameterized inputs rather than duplicating either multi-step workflow skill.

The prompt requires the user to identify a notebook and findings file. It then:

- Reads both sources before drafting and preserves their reported values without invention, estimation, or silent correction.
- Uses a fixed issue structure covering context, exact parameters, measured results, the researcher's first-person surprise, and proposed labels.
- Includes implementation artifacts only when they materially affect interpretation and omits broader issue-workflow sections unless requested.
- Preserves intentional edits in an existing draft, validates the completed content against the sources, and saves it locally without publishing the issue.

This division keeps the prompt centered on one repeatable research-writing task while the skills retain broader Git and issue-linked workflow responsibilities.

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