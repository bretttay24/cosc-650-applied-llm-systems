# COSC 650: Applied LLM Systems

Week-by-week implementations of applied LLM systems, covering tokenization, inference and sampling, prompt engineering, function/tool calling, retrieval-augmented generation, fine-tuning, and evaluation.

## Course Context

COSC 650 is an eight-week graduate course in the M.S. in Artificial Intelligence program at Maryville University. The assignments are based in Jupyter Notebooks / Google Colab and submitted through GitHub, reviewed through pull requests, and revised in response to feedback. 

The repository is built to be read by humans and LLMs. The hope is to be disciplined in documentation so that our memoryless assistants can have rich context for key decisions and rationale. GitHub Issues will be thorough, commit messages reference the issues they resolve, and `CLAUDE.md` at the root gives an AI assistant the project's structure and conventions at the start of every session. The goal is to use thorough GitHub documentation as infrastructure for providing our LLMs context.

## Weekly Modules

| Week | Topic |
|------|-------|
| 00 | Setup | 
| 01 | Tokenization and text representation | 
| 02 | Architecture, inference, and sampling | 
| 03 | Systematic prompt engineering | 
| 04 | Function calling and tool use | 
| 05 | Retrieval-augmented generation foundations | 
| 06 | Advanced RAG and knowledge systems | 
| 07 | Fine-tuning and adaptation | 
| 08 | Evaluation, testing, QA, and integration |

## Repo Structure

```
week-NN/                Weekly assignments and notebooks for each of the 8 weeks
notes/                  Reading annotations and research notes
capstone/               Week 8 integrated system: code, evals, and documentation
CLAUDE.md               Project context and conventions, read by AI assistants
README.md               This file
```

## Technologies

- **Python 3.11+** for all code
- **Jupyter / Google Colab** for notebooks
- **tiktoken** for tokenization experiments
- **OpenAI and Anthropic SDKs** for model access and function calling
- **Vector search and embedding libraries** for the RAG work in weeks 5 and 6
- Additional libraries added per week as the material calls for them



## Author

Brett — M.S. Artificial Intelligence candidate, Maryville University (December 2026)