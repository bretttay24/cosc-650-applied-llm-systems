# GitHub Context Infrastructure

This directory contains version-controlled context and workflow customizations used while completing the course. They are part of the repository's applied LLM systems work: instead of supplying every expectation in an ad hoc chat prompt, the repository makes important context repeatable, task-aware, reviewable, and available to other coding-agent sessions.

These files do not replace critical review of model output. They provide a documented starting point for how an assistant should understand the project, interact with notebooks, and support recurring development tasks.

## Current Layers

| Primitive | Role | Repository implementation | Activation | Why it is used |
|---|---|---|---|---|
| Agent instructions | Shared project structure and conventions for coding agents | [`../AGENTS.md`](../AGENTS.md) | Loaded as repository-level context | Keeps environment, workflow, and safety conventions in one cross-agent source of truth |
| Copilot instructions | GitHub Copilot's repository-wide instruction entry point | [`copilot-instructions.md`](copilot-instructions.md) | Applied to Copilot requests in this repository | Directs Copilot to `AGENTS.md` without maintaining duplicate guidance |
| Path-specific instructions | Rules that apply to matching files or tasks | [`instructions/local-jupyter.instructions.md`](instructions/local-jupyter.instructions.md) | Its `applyTo` pattern matches `week-*/*.ipynb` | Constrains notebook work to local Jupyter and UV while protecting secrets and reproducibility |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/commit-message/SKILL.md`](skills/commit-message/SKILL.md) | Selected when a request matches its description | Drafts an issue-linked commit message from staged changes without taking unrelated Git actions |
| Agent skill | On-demand guidance for a specialized, multi-step workflow | [`skills/issue-linked-git-workflow/SKILL.md`](skills/issue-linked-git-workflow/SKILL.md) | Selected when a request matches its description | Connects issue, branch, commit, and pull request conventions while keeping publication manual |
| Prompt file | A focused reusable task invoked manually in VS Code Copilot Chat | Planned location: `prompts/*.prompt.md` | Invoked by its slash command or from the editor | Planned for Week 2; no prompt files have been implemented yet |

## How the Layers Work Together

When an assistant works on a weekly notebook, `AGENTS.md` supplies the repository-wide conventions and `copilot-instructions.md` provides the Copilot-specific entry point. Because the target matches `week-*/*.ipynb`, the local Jupyter instructions add notebook-specific constraints such as using the UV-managed environment, keeping credentials out of source and output, and executing the notebook from top to bottom.

The workflow skills are used only when the task calls for them. For example, preparing a commit message loads the staged-change rules in the `commit-message` skill, while drafting or validating an issue-linked workflow uses the broader `issue-linked-git-workflow` skill. Keeping these procedures out of always-on instructions avoids adding task-specific context to unrelated notebook work.

## Week 2 Prompt Experiment

Week 2 will explore how both current skills could be represented as `.prompt.md` files:

- `commit-message` will be examined as a focused, manually invoked prompt for producing a commit command from staged changes.
- `issue-linked-git-workflow` will be examined as a prompt for issue, branch, and pull request workflow support.

The purpose is comparison, not a predetermined migration. The experiment will consider how much of each workflow remains clear and reusable as a prompt, what is gained through explicit invocation and parameterized input, and what may be lost from skill discovery, multi-step guidance, or bundled workflow context. The results will inform when this repository should use instructions, prompts, or skills.

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