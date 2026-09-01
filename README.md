# COSC 650: Applied LLM Systems

Week-by-week implementations of applied LLM systems, covering tokenization, inference and sampling, prompt engineering, function/tool calling, retrieval-augmented generation, fine-tuning, and evaluation.

## Course Context

COSC 650 is an eight-week graduate course in the M.S. in Artificial Intelligence program at Maryville University. The assignments are developed in local Jupyter Notebooks and submitted through GitHub, reviewed through pull requests, and revised in response to feedback.

The repository is built to be read by humans and LLMs. The goal is disciplined documentation that gives assistants rich context for key decisions and rationale. GitHub Issues are thorough, commits and pull requests reference the issues they resolve, and `AGENTS.md` at the root gives an AI assistant the project's structure and conventions at the start of every session.

## Applied Context Infrastructure

The repository also treats context engineering as part of applied LLM systems work. Version-controlled instructions give coding agents durable project conventions, path-specific guidance constrains how they interact with course notebooks, and agent skills package recurring GitHub workflow tasks. This makes the context supplied to an assistant visible, reviewable, and reusable instead of relying only on ad hoc chat prompts.

In Week 2, both existing .github/skills will also be explored as `.prompt.md` files. Comparing the same tasks as skills and manually invoked prompts will help clarify which format is better suited to focused requests, multi-step workflows, and automatic discovery. See the [`.github` context infrastructure guide](.github/CONTEXT_INFRASTRUCTURE.md) for definitions, the current implementation, and the experiment roadmap.

## Weekly Modules

| Week | Topic |
|------|-------|
| 0 | Setup |
| 1 | Tokenization and text representation |
| 2 | Architecture, inference, and sampling |
| 3 | Systematic prompt engineering |
| 4 | Function calling and tool use |
| 5 | Retrieval-augmented generation foundations |
| 6 | Advanced RAG and knowledge systems |
| 7 | Fine-tuning and adaptation |
| 8 | Evaluation, testing, QA, and integration |

## Repo Structure

```
.github/                Context instructions, prompts, and workflow skills
week-N/                 Setup and weekly assignments (weeks 0 through 8)
notes/                  Reading annotations and research notes
project/                Final project code and documentation
AGENTS.md               Project context and conventions, read by AI assistants
README.md               This file
```

The [`.github` context infrastructure guide](.github/CONTEXT_INFRASTRUCTURE.md) explains how each customization supports the coursework.

## Technologies

- **Python 3.14+** for all code
- **VS Code** for development
- **Local Jupyter** for notebooks
- **GitHub Copilot in VS Code** for AI-assisted development
- **UV** for Python dependency and environment management
- **tiktoken** for tokenization experiments
- **OpenAI and Anthropic SDKs** for model access and function calling
- **Vector search and embedding libraries** for the RAG work in weeks 5 and 6
- Additional libraries added per week as the material calls for them

## Documented Workflow

1. Create a GitHub Issue that describes the problem or task.
2. Create a branch for that issue: `git checkout -b BT_2`. (`<initials>_<issue number>`)
3. Implement the work in the branch, including relevant tests and documentation.
4. Commit with a descriptive, issue-linked message, for example: `git commit -m "Improve boundary detection" -m "Refs #2"`.
5. Push the branch: `git push -u origin BT_2`.
6. Open a pull request that explains what changed, why it changed, and how it was validated. Include `#2` in the pull request to link it to issue #2.
7. Address review comments, merge the approved pull request into `main`, and delete the branch.

A bare `#2` references/links to an issue but does not close it. GitHub closes the issue when a supported closing keyword, such as `Fixes #2`, appears in the merged pull request or commit.

## Author

Brett — M.S. Artificial Intelligence candidate, Maryville University (December 2026)