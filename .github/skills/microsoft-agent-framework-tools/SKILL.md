---
name: microsoft-agent-framework-tools
description: "Build, refactor, and review Python function tools for Microsoft Agent Framework. Use when creating MAF @tool functions, replacing hand-written JSON tool definitions, adding Pydantic input schemas, documenting parameters with Annotated and Field, constraining choices with Literal, validating arguments, handling tool errors, wiring automatic function invocation, or testing model-facing tool schemas."
license: MIT
metadata:
  author: Brett Taylor
  version: "1.1"
---

# Microsoft Agent Framework Tools

Build clear, constrained, and testable Python function tools for Microsoft Agent Framework (MAF). Prefer Pydantic-backed tools because they provide both a model-facing JSON Schema and runtime validation of model-supplied arguments.

Use this skill for individual tools, related toolboxes, and migrations from manually maintained JSON function definitions. Preserve existing tool behavior unless the user requests a behavior change.

## Core Pattern

Use:

- `@tool` from `agent_framework`.
- An explicit Pydantic `BaseModel` passed through `schema=`.
- `Annotated[T, Field(...)]` for model-facing parameter descriptions and constraints.
- `Literal[...]` for a closed set of supported values.
- `ConfigDict(extra="forbid", strict=True)` when strict input validation is appropriate.
- Fields without defaults for required arguments.
- Explicit defaults only for genuinely optional arguments.
- Stable, JSON-serializable return values.

Avoid raw JSON schema dictionaries by default. Use one only when the user explicitly requests it or the tool is trusted and non-sensitive and lightweight top-level validation is sufficient.

## Author Preferences

- Follow the documented Microsoft Agent Framework pattern before introducing additional abstractions.
- Define the Pydantic model, `Annotated` aliases, and decorated function in the same module as the tool.
- Keep shared non-Pydantic state, such as a ledger used by several tools, in a separate state module when needed.
- Prefer directly decorated module-level functions over tool factories, wrapper classes, or nested functions.
- Do not create a factory whose only purpose is to return a decorated function.
- Keep simple `Annotated` and `Field` declarations on one line, even when the line is longer than a typical formatter target.
- Flatten short function signatures when they remain readable; prefer a compact signature, one-line docstring, and implementation.
- Add concise function docstrings.
- Use constraints expressible through `Field` and `Literal` before considering custom validation.
- Do not add `field_validator`, `model_validator`, runtime context, custom result parsers, or other advanced patterns unless the tool's stated requirements need them.
- Do not expand the task into authorization or approval-policy design unless the user explicitly asks for that scope.

## Workflow

### 1. Inspect the Existing Tool

Before editing:

1. Read the function, its callers, tests, and agent registration.
2. Identify every model-supplied parameter.
3. Identify shared types or constraints that can be reused.
4. Record the current return shape and expected exceptions.
5. Find hand-written tool-definition dictionaries that the decorated callable will replace.
6. Check the installed Agent Framework and Pydantic versions before relying on version-specific APIs.

Keep tool logic and state out of notebook cells. The notebook should import and register the tools. If several tools share simple state, place that state in a separate module and import the same instance into each tool module.

### 2. Design the Input Contract

For each parameter, specify:

- Python type.
- Whether it is required.
- Model-facing description.
- Allowed values.
- Numeric, string, collection, or pattern constraints.
- Any relationship to other fields.

Prefer reusable annotated aliases when multiple schemas use the same concept:

```python
from typing import Annotated, Literal

from pydantic import Field

GroupBy = Annotated[Literal["label", "confidence"], Field(description="The recorded field used to group the results.")]
```

Use `Literal`, not a Python `Enum`, when the requested contract is a small closed set of string or numeric values. Pydantic will represent a `Literal` as an `enum` in the generated JSON Schema; this is expected.

### 3. Create the Pydantic Schema

Define a dedicated input model:

```python
from pydantic import BaseModel, ConfigDict


class SummaryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    group_by: GroupBy
```

Follow these rules:

- Use a descriptive `<ToolName>Input` class name.
- Set `extra="forbid"` so undeclared model arguments are rejected.
- Use strict validation when implicit coercion would make the contract ambiguous.
- Omit a default to make a field required.
- Use `None` only when `None` is a meaningful supported value.
- Add `min_length`, `max_length`, `ge`, `le`, `pattern`, or collection bounds when they represent real requirements.
- Do not add arbitrary constraints that are unsupported by the tool's behavior.

Do not add a custom Pydantic validator when `Field`, `Literal`, and the normal function implementation already satisfy the requirement. Add one only when a stated rule cannot be represented by those simpler documented patterns.

### 4. Decorate the Function

Use an explicit name, concise description, and Pydantic schema:

```python
from agent_framework import tool


@tool(
    name="get_summary",
    description=(
        "Return deterministic counts and percentages from the existing "
        "classification ledger without modifying it."
    ),
    schema=SummaryInput,
)
def get_summary(group_by: GroupBy) -> dict[str, object]:
    """Summarize the recorded results by the selected field."""
    return LEDGER.summarize(group_by)
```

The decorator description should explain:

- What the tool accomplishes.
- When the agent should select it.
- Important boundaries or prerequisites.
- Whether it reads or changes the data relevant to its task.

Parameter descriptions belong in `Annotated[..., Field(description=...)]`. Do not rely on parameter names alone to teach the model how to call a tool.

Keep the function signature compatible with the schema:

- Use matching names.
- Use compatible Python types.
- Keep required and optional status consistent.
- Do not expose implementation dependencies as model arguments.

Do not wrap the tool in a `create_*_tool` factory solely to capture shared state. Prefer a directly decorated function that imports the shared state it uses:

```python
@tool(name="get_summary", description="...", schema=SummaryInput)
def get_summary(group_by: GroupBy) -> dict[str, object]:
    """Summarize the recorded results by the selected field."""
    return LEDGER.summarize(group_by)
```

### 5. Implement Predictable Results and Errors

Return small, stable, JSON-serializable values. Prefer a consistent result shape across related tools.

Use a structured result for expected domain outcomes:

```python
return {
    "ok": False,
    "error": {
        "code": "no_records",
        "message": "No records are available to summarize.",
        "retryable": False,
    },
}
```

Raise a specific exception when valid execution cannot continue:

```python
raise ValueError(f"comment_id already recorded: {comment_id}")
```

Do not:

- Catch every exception and return a success-shaped value.
- Return stack traces or raw exception objects.
- Include secrets, credentials, or sensitive internal details in model-visible errors.
- Silently replace invalid input with a default.
- Use `eval`, `exec`, or model-supplied source code to implement a function tool.

Agent Framework converts argument-validation and execution failures into tool-error results during automatic invocation. Keep detailed errors disabled for model-visible channels unless the user explicitly establishes a trusted debugging context.

Use a Pydantic output model when a stable result contract benefits callers or tests. Use a `result_parser` only when the default serialization does not produce an appropriate tool result.

### 6. Register the Decorated Callable

Register the decorated function itself:

```python
tools = [
    record_classification,
    get_summary,
    plot_distribution,
]
```

Remove obsolete `*_tool` JSON dictionaries and any custom dispatcher logic that exists only to reproduce framework behavior, after confirming no remaining caller depends on it.

MAF's automatic invocation flow covers:

1. Sending tool definitions to the model.
2. Detecting requested calls.
3. Parsing and validating arguments.
4. Executing the matching callable.
5. Returning the tool result to the conversation.
6. Allowing the model to continue.

When related tools share mutable state or depend on model-requested order, configure sequential invocation:

```python
client.function_invocation_configuration["allow_concurrent_invocation"] = False
```

Use bounded automatic invocation so an invalid or repetitive call sequence cannot continue indefinitely:

```python
client.function_invocation_configuration.update(
    {
        "max_iterations": 5,
        "max_function_calls": 20,
        "max_duration_seconds": 30.0,
    }
)
```

Choose bounds appropriate to the application rather than copying these example values without review.

### 7. Validate the Tool

Inspect the generated JSON Schema and test runtime behavior.

Confirm that:

- Every property has the intended JSON type.
- Required fields appear in `required`.
- `Literal` choices appear as `enum`.
- `additionalProperties` is `false`.
- Field descriptions are present and accurate.
- Defaults appear only for optional parameters.
- Valid arguments invoke the function.
- Missing required arguments fail.
- Extra arguments fail.
- Invalid literal values fail.
- Wrong primitive types fail when strict validation is enabled.
- Field and cross-field constraints fail with useful validation messages.
- Execution exceptions become safe tool errors.
- Return values serialize successfully.
- The agent can consume a tool result and continue.

Run the smallest existing test or example that covers the modified tools. Add focused tests when the repository has a test structure.

## Review Checklist

- [ ] `@tool` is imported from `agent_framework`.
- [ ] A Pydantic input model is passed explicitly with `schema=`.
- [ ] `Annotated` and `Field` describe model-supplied parameters.
- [ ] Closed choices use `Literal`.
- [ ] Required fields have no defaults.
- [ ] Unexpected properties are forbidden.
- [ ] Constraints reflect actual function behavior.
- [ ] The Pydantic model and annotated fields are colocated with the tool.
- [ ] Simple declarations and function signatures are compact.
- [ ] Custom validators and factories are absent unless required.
- [ ] The function signature matches the schema.
- [ ] The result is stable and JSON serializable.
- [ ] Expected failures have structured, actionable results.
- [ ] Unexpected failures are not hidden or exposed in unsafe detail.
- [ ] The decorated callable, not a legacy schema dictionary, is registered.
- [ ] Shared-state tools use an appropriate invocation order.
- [ ] Generated schema and runtime validation are tested.

## Reference

Follow the current Microsoft documentation for version-specific APIs:

<https://learn.microsoft.com/en-us/agent-framework/agents/tools/function-tools?pivots=programming-language-python>
