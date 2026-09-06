# Agents.md

## Project
Course repository for COSC 650: Applied LLM Systems (Maryville University).
8-week graduate course covering tokenization, transformer architecture,
prompt engineering, function/tool calling, retrieval-augmented generation, fine-tuning, and evaluation.

## Structure
- week-00/ through week-08/ : weekly assignments and notebooks
- notes/ : research notes and reading annotations
- project/ : final project code and documentation
- AGENTS.md : this file
- README.md : human-facing project description

## Conventions
- Use local Jupyter Notebooks (`.ipynb`) and commit them to the repository; do not use or add Google Colab integration.
- All code is Python 3.14+.
- Use UV for dependency management and project commands, including `uv sync` and `uv run`.
- Store API keys and other environment variables in the local `.env` file; load them with `python-dotenv` when needed.
- tiktoken is used for tokenization experiments
- Begin work with a GitHub Issue, then create a branch named `<developer_initials>_<issue-number>`, such as `BT_2`.
- Make focused changes that include relevant tests and documentation.
- Use descriptive, imperative commit messages that reference the issue. Each message should complete the sentence: "If applied, this commit will ___." For example: `Add token-count tests`.
- Open a pull request for review before merging.


## Do Not
- Delete files or directories without confirming first
- Delete branches
- Push directly to `main`
- Commit API keys or any file in .env

## AI Usage (Disclose per Course Policy)
### Week 2 
Github Copilot was used to:
* Help make GH commit messages, primarily with `GPT-5.6 Luna`
* Edit my hand typed analysis making it more consice  `GPT - 5.6 Terra`
* Generate code for matplotlib visuals based on my description / decisions of variables and structure
* Summarize my findings and my analysis and create the `findings.md`
* Generate first draft of research GH issue. 
* After working this process generated `.github\prompts\research-finding-issue.prompt.md` 
* Update `.github\CONTEXT_INFRASTRUCTURE.md`