# Prompt Library

This folder stores versioned prompt text and the configuration needed to load each prompt consistently.

## Structure

```text
prompts/
├── loader.py
├── <prompt-name>/
│   ├── metadata.yaml
│   ├── v1.txt
│   ├── v2.txt
│   ├── prompt-changelogs/       # Version-specific revision records
│   │   └── v2.md
│   └── evaluation-results/       # Optional evaluation exports
│       └── ...
└── <another-prompt-name>/
    ├── metadata.yaml
    └── v1.txt
```

Each prompt has its own directory. The directory name is the prompt name passed to the loader. Prompt versions are plain-text files named `<version>.txt`, such as `v1.txt` or `v2.txt`.

## `metadata.yaml`

`metadata.yaml` configures a prompt and selects its default version. For example:

```yaml
name: hcahps-classifier
active_version: v2
model: gpt-4o
params:
  temperature: 0.2
  max_output_tokens: 450
description: |
  Classify HCAHPS survey responses into categories with a rationale and confidence level.
```

Required fields used by `loader.py` are:

| Field | Purpose |
| --- | --- |
| `active_version` | Version loaded when the caller does not specify one. It must match a `<version>.txt` filename. |
| `model` | Model identifier included in the loaded prompt configuration. |
| `params` | Mapping of model parameters, such as `temperature` and `max_output_tokens`. |

`name` and `description` are documentation fields. The loader identifies a prompt from its directory name, not the `name` value in this file.

## Loading Prompts

Use `load()` from `loader.py` with the prompt directory name:

```python
from loader import load

prompt = load("hcahps-classifier")

print(prompt.version)  # "v2", from active_version
print(prompt.text)  # Contents of hcahps-classifier/v2.txt
print(prompt.model)  # "gpt-4o"
print(prompt.params)  # {"temperature": 0.2, "max_output_tokens": 450}
```

Pass a version explicitly to load a non-active version for testing or evaluation:

```python
baseline = load("hcahps-classifier", version="v1")
```

The loader returns an immutable `Prompt` object with `name`, `text`, `version`, `model`, and `params` attributes.

## Prompt Change Logs

Record the rationale and measured effects of each prompt revision in `<prompt-name>/prompt-changelogs/`. Create one Markdown file per version, named `<version>.md`; for example, the changes for `v2.txt` belong in `prompt-changelogs/v2.md`.

Use this structure:

```markdown
## v2 (MM-DD-YYYY)

**Changed:** What changed in the prompt.

**Reason:** Why the revision was needed, ideally based on evaluation findings.

**Impact:** How quality, cost, latency, token usage, or other relevant measures changed.

**Eval:** The evaluation data, test suite, and metrics used to compare versions.
```

The change log complements the versioned prompt text: `.txt` files contain the prompt that runs, while the matching `.md` file preserves the decision record and evidence for that version. Add the change log when adding a new prompt version, before updating `active_version` to make it the default.

## Adding a Prompt or Version

1. Create a directory named for the prompt, for example `prompts/my-classifier/`.
2. Add `metadata.yaml` with `active_version`, `model`, and `params`.
3. Add the selected version file, such as `v1.txt`, and its matching `prompt-changelogs/v1.md` record.
4. When revising a prompt, add a new file such as `v2.txt` and `prompt-changelogs/v2.md`, then update `active_version` only after it is ready to become the default.

An explicit version must correspond to an existing `.txt` file. Missing metadata files, required metadata keys, or version files cause `load()` to raise the underlying file or key error.
