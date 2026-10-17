from typing import Annotated

from agent_framework import FunctionInvocationContext, tool
from pydantic import BaseModel, ConfigDict, Field

from .ledger import GroupBy, get_session_ledger

SummaryGroupByField = Annotated[GroupBy, Field(description="The recorded field used to group the summary results.")]


class GetSummaryInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    group_by: SummaryGroupByField


@tool(
    name="get_summary",
    description=(
        "Return deterministic counts and percentages from the existing patient-comment "
        "ledger. Use this to report recorded results grouped by "
        "label or confidence. This tool does not modify the ledger."
    ),
    schema=GetSummaryInput,
)
def get_summary(group_by: SummaryGroupByField, context: FunctionInvocationContext) -> dict[str, object]:
    """Summarize recorded comment themes by label or confidence."""
    return get_session_ledger(context.session).summarize(group_by)
