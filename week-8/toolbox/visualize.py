from pathlib import Path
from typing import Annotated

import matplotlib.pyplot as plt
from agent_framework import FunctionInvocationContext, tool
from matplotlib.ticker import MaxNLocator
from mlflow import start_span
from mlflow.entities import SpanType
from mlflow.tracing.attachments import Attachment
from pydantic import BaseModel, ConfigDict, Field

from .ledger import GroupBy, get_session_ledger

PlotGroupByField = Annotated[GroupBy, Field(description="The recorded field shown on the chart's category axis.")]


class PlotDistributionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    group_by: PlotGroupByField


@tool(
    name="plot_distribution",
    description=(
        "Create a bar-chart artifact from recorded patient-comment themes. "
        "Use this to visualize results grouped by label or confidence. This "
        "tool reads the existing ledger and does not modify it."
    ),
    schema=PlotDistributionInput,
)
def plot_distribution(group_by: PlotGroupByField, context: FunctionInvocationContext) -> dict[str, object]:
    """Create a bar chart from classifications in the session ledger."""
    summary = get_session_ledger(context.session).summarize(group_by)

    if summary["total_comments"] == 0:
        return {"created": False, "message": "No recorded classifications are available to plot.", "summary": summary}

    counts_by_category = summary["counts"]
    if not isinstance(counts_by_category, dict):
        raise TypeError("summary counts must be a dictionary")

    labels = list(counts_by_category)
    counts = list(counts_by_category.values())

    if context.session is None:
        raise RuntimeError("Plotting classifications requires an active agent session")

    artifact_directory = Path("artifacts") / context.session.session_id
    artifact_directory.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_directory / f"hcahps_{group_by}_distribution.png"

    with start_span(name="plot_artifact", span_type=SpanType.CHAIN) as span:
        span.set_inputs({"group_by": group_by, "category_count": len(labels)})

        figure, axis = plt.subplots(figsize=(10, 5))
        axis.bar(labels, counts, color="#2a6f97")
        axis.set_title(f"Patient Comment Theme Distribution by {group_by.title()}")
        axis.set_xlabel(group_by.title())
        axis.set_ylabel("Recorded Comments")
        axis.yaxis.set_major_locator(MaxNLocator(integer=True))
        axis.tick_params(axis="x", rotation=30)
        figure.tight_layout()
        figure.savefig(artifact_path, dpi=150)
        plt.close(figure)

        span.set_outputs({"plot": Attachment.from_file(artifact_path), "summary": summary})

    return {"created": True, "artifact_path": str(artifact_path), "summary": summary}
