# Microsoft Agent Framework Toolbox

This directory adapts the deterministic tools developed during Week 4 for use with Microsoft Agent Framework (MAF).

Week 4 introduced the core function-calling practices used here:

- Give each tool a clear purpose and model-facing description.
- Define explicit argument types and required fields.
- Restrict closed choices to supported values.
- Reject unexpected arguments.
- Validate model-supplied arguments before execution.
- Return tool results to the conversation so the model can continue.
- Represent invalid arguments and execution failures clearly.

Those principles remain the same. The implementation changes from manually maintained JSON tool definitions and a custom function-calling loop to MAF's `@tool` decorator, automatic function invocation, and Pydantic-backed input schemas.

## Why Pydantic

Microsoft Agent Framework accepts either a Pydantic model or a raw JSON schema dictionary for an explicit tool schema. A raw dictionary receives lightweight top-level checks and is best suited to a trusted, non-sensitive tool. The tools in this directory use Pydantic because it provides runtime enforcement in addition to the schema shown to the model.

Pydantic provides:

- Runtime validation of model-supplied arguments.
- Generated JSON Schema for the model.
- Rejection of undeclared properties.
- Required and optional field handling.
- Numeric, string, pattern, and collection constraints.
- Field-level and cross-field validators.
- Conversion to validated Python values when supported by the schema.

Each Pydantic input model is defined in the same module as its tool. One shared
`LEDGER` remains separate because all three tools operate on the same state.

The tool input models use:

- `BaseModel` to define the complete input contract.
- `ConfigDict(extra="forbid", strict=True)` to reject extra arguments and avoid ambiguous coercion.
- `Annotated` with `Field` to give each parameter a precise description and any applicable constraints.
- `Literal` to define closed sets of supported values without creating Python enum classes.

For example:

```python
from typing import Annotated, Literal

from agent_framework import tool
from pydantic import BaseModel, ConfigDict, Field

GroupBy = Annotated[
    Literal["label", "confidence"],
    Field(description="The recorded field used to group the results."),
]


class SummaryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    group_by: GroupBy


@tool(
    name="get_summary",
    description=(
        "Return deterministic counts and percentages from the existing "
        "classification ledger without modifying it."
    ),
    schema=SummaryInput,
)
def get_summary(group_by: GroupBy) -> dict[str, object]:
    ...
```

`Literal["label", "confidence"]` appears as an `enum` in the generated JSON Schema. This is expected: `Literal` is the Python type declaration, while `enum` is the corresponding JSON Schema representation.

## Agent Framework Function Calling

The Week 4 implementation demonstrated the complete function-calling loop directly:

1. Send tool definitions to the model.
2. Intercept requested tool calls.
3. Parse and validate arguments.
4. Execute the selected function.
5. Return its result to the conversation.
6. Let the model continue.

MAF performs this same flow through automatic function invocation. The notebook imports the shared ledger and the three decorated callables:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("week-8").resolve()))

from toolbox import LEDGER, TOOLS

LEDGER.clear()
```

This removes duplicated schema definitions and custom dispatch logic while preserving the Week 4 learning goals.

The notebook is the composition layer: it passes `TOOLS` to the agent and may
clear the ledger before a new experiment. Ledger storage and deterministic tool
behavior stay in this package so they can be tested without notebook globals.

## Errors and Results

Argument-validation failures and execution exceptions become tool-error results during automatic invocation. Detailed internal exceptions should remain unavailable to model-visible channels by default.

Expected domain outcomes should use a stable, structured response:

```python
{
    "ok": False,
    "error": {
        "code": "no_records",
        "message": "No records are available to summarize.",
        "retryable": False,
    },
}
```

Unexpected failures should raise a specific exception rather than returning a success-shaped result. Tool results must remain small, predictable, and JSON serializable.

## Validation Expectations

Each tool should be checked for:

- Correct generated property types.
- Required fields.
- `Literal` choices represented as JSON Schema `enum` values.
- `additionalProperties: false`.
- Complete field descriptions.
- Rejection of missing, extra, or invalid arguments.
- Safe handling of execution failures.
- Serializable return values.
- Successful continuation of the agent after a tool result.

## Reference

The implementation follows the Python function-tool guidance in the Microsoft Agent Framework documentation:

<https://learn.microsoft.com/en-us/agent-framework/agents/tools/function-tools?pivots=programming-language-python>
