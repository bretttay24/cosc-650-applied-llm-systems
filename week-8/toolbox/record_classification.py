from typing import Annotated

from agent_framework import tool
from pydantic import BaseModel, ConfigDict, Field

from .ledger import LEDGER, ConfidenceLevel, HcahpsTheme

CommentIdField = Annotated[int, Field(ge=1, description="The positive integer ID for the patient comment.")]
HcahpsThemeField = Annotated[HcahpsTheme, Field(description="The single primary HCAHPS-aligned theme for the patient comment.")]
ConfidenceField = Annotated[ConfidenceLevel, Field(description="Confidence in the label: low for vague, medium for competing, or high for clear cases.")]
RationaleField = Annotated[str, Field(min_length=1, description="One or two sentences citing or paraphrasing the comment language that supports the label.")]


class RecordClassificationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    comment_id: CommentIdField
    label: HcahpsThemeField
    confidence: ConfidenceField
    rationale: RationaleField


@tool(
    name="record_classification",
    description=(
        "Record one model-selected HCAHPS-aligned feedback theme in the "
        "classification ledger. Use this only after choosing the primary theme "
        "for a patient comment. This tool records but does not classify text."
    ),
    schema=RecordClassificationInput,
)
def record_classification(comment_id: CommentIdField, label: HcahpsThemeField, confidence: ConfidenceField, rationale: RationaleField) -> dict[str, int | str]:
    """Record one validated feedback-theme classification in the shared ledger."""
    return LEDGER.record(comment_id, label, confidence, rationale)
