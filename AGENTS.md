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
- Make focused changes that include relevant tests and documentation.
- Use descriptive, imperative commit messages. Reference an issue when one applies. Each message should complete the sentence: "If applied, this commit will ___." For example: `Add token-count tests`.
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

### Week 3
Github Copilot was used to:
* Help make GH commit messages
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft
* Generate prompt test-suite inputs and outputs, which I verified

### Week 4
Github Copilot was used to:
* Help make GH commit messages
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft

### Week 5
Github Copilot was used to:
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft

### Week 6
Github Copilot was used to:
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft

### Week 7
Github Copilot was used to:
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft
* Microsoft Foundry Synthetic Datasets for Fine tuning were created with GPT-5.4

### Week 8
Github Copilot was used to:
* Edit my hand typed analysis, making it more concise and grammatically correct
* Generate portions of code based on requested analysis
* Summarize findings and create the `findings.md`
* Use `research-finding-issue.prompt.md` to create the first draft of a research GH issue
* Use `issue-linked-git-workflow/SKILL.md` to create the PR draft
