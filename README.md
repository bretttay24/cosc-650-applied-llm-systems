# COSC 650: Applied LLM Systems

Week-by-week implementations of applied LLM systems, covering tokenization, inference and sampling, prompt engineering, function/tool calling, retrieval-augmented generation, fine-tuning, and evaluation.

## Course Context

COSC 650 is an eight-week graduate course in the M.S. in Artificial Intelligence program at Maryville University. The assignments are developed in local Jupyter Notebooks and submitted through GitHub, reviewed through pull requests, and revised in response to feedback.

The repository is built to be read by humans and LLMs. The goal is disciplined documentation that gives assistants rich context for key decisions and rationale. After each assignment, `findings.md` records the measured results and analysis, GitHub Issues preserve the primary findings as research notes, and pull requests link the completed work to those notes. `AGENTS.md` at the root gives an AI assistant the project's structure and conventions at the start of every session. It also discloses each week's AI usage under the COSC 650 course policy.

## Applied Context Infrastructure

The repository also treats context engineering as part of applied LLM systems work. Version-controlled instructions give coding agents durable project conventions, path-specific guidance constrains how they interact with course notebooks, and agent skills package recurring GitHub workflow tasks. This makes the context supplied to an assistant visible, reviewable, and reusable instead of relying only on ad hoc chat prompts.


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
| 8 | Evaluation, testing, QA, integration, and the final course capstone project (located in `week-8/`) |

## Repo Structure

```
.github/                Context instructions, prompts, and workflow skills
docker/                 Local PostgreSQL/pgvector service for RAG
week-N/                 Setup and weekly assignments (weeks 0 through 8)
AGENTS.md               Project context and conventions, read by AI assistants
README.md               This file
```

The [`.github` context infrastructure guide](.github/CONTEXT_INFRASTRUCTURE.md) explains how each customization supports the coursework.

## Technologies

- **Python 3.14+** for all code
- **VS Code** for development
- **Local Jupyter** for notebooks
- **GitHub Copilot in VS Code** for AI-assisted development (see .github/ and AGENTS.md)
- **UV** for Python dependency and environment management
- **tiktoken** for tokenization experiments
- **OpenAI, Azure OpenAI, and models hosted in Microsoft Foundry** for generation, tool use, embeddings, synthetic data generation, and evaluation
- **`all-MiniLM-L6-v2`** for local embeddings and **`text-embedding-3-small`** hosted in Microsoft Foundry for hosted embeddings
- **PostgreSQL with pgvector in Docker** as the local vector database for the RAG work
- **Reciprocal Rank Fusion (RRF)** adapted from Adrian Raudaschl's [RAG-Fusion](https://github.com/Raudaschl/rag-fusion) implementation for combining ranked retrieval results
- **Jev System One reranking**, based on the [RAG-Fusion Jev experiment](https://github.com/Raudaschl/rag-fusion/tree/master/experiments/jev-in-the-pipeline) and Adam Hevenor's [hev reranker](https://github.com/hev/reranker), for rescoring candidates by estimated relevance
- Additional libraries added per week as the material calls for them


## Author

Brett — M.S. Artificial Intelligence candidate, Maryville University (December 2026)