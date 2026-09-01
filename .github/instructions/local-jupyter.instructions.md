---
name: "Local Jupyter Notebooks"
description: "Use when creating or editing Jupyter notebooks. Enforces local Jupyter, UV dependency management, and reproducible notebook execution."
applyTo: "week-*/*.ipynb"
---
# Local Jupyter Notebook Guidelines

- Only add or change code inside code cells marked `TODO (you)`. Treat all other code cells as provided and read-only.
- Target local Jupyter running in the repository's UV-managed Python 3.14+ environment.
- Do not add Google Colab integration, Colab badges, Drive mounts, or Colab-specific setup instructions.
- Leave existing Colab-specific starter content unchanged unless the user explicitly asks to remove it.
- Manage notebook dependencies in `pyproject.toml` with UV. Do not add notebook cells that run `pip install` or other package-install commands.
- Use environment variables from the local `.env` file through `python-dotenv` when credentials are needed. Never place secrets in notebook source or output.
- Keep notebooks runnable from the repository root after `uv sync` and select the repository's virtual-environment kernel.
- Before considering notebook changes complete, execute all cells from top to bottom and confirm they succeed without hidden state.