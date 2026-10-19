from collections import Counter
from typing import Literal, TypedDict

from agent_framework import AgentSession

HcahpsTheme = Literal[
    "communication_nurses",
    "communication_doctors",
    "staff_responsiveness",
    "communication_medicines",
    "discharge_information",
    "care_transition",
    "cleanliness",
    "quietness",
    "other",
]
ConfidenceLevel = Literal["low", "medium", "high"]
GroupBy = Literal["label", "confidence"]
SESSION_LEDGER_KEY = "classification_ledger"


class ClassificationEntry(TypedDict):
    label: HcahpsTheme
    confidence: ConfidenceLevel
    rationale: str


class ClassificationLedger:
    """Store and summarize comment-theme classifications for one agent session."""

    def __init__(self) -> None:
        """Initialize an empty classification ledger."""
        self._entries: dict[int, ClassificationEntry] = {}

    def __len__(self) -> int:
        """Return the number of recorded classifications."""
        return len(self._entries)

    def clear(self) -> None:
        """Remove all recorded classifications from the ledger."""
        self._entries.clear()

    def get(self, comment_id: int) -> ClassificationEntry:
        """Return the recorded classification for one comment."""
        return self._entries[comment_id].copy()

    def record(self, comment_id: int, label: HcahpsTheme, confidence: ConfidenceLevel, rationale: str) -> dict[str, int | str]:
        """Record one classification and return its updated ledger counts."""
        if comment_id in self._entries:
            raise ValueError(f"comment_id already recorded: {comment_id}")

        self._entries[comment_id] = {"label": label, "confidence": confidence, "rationale": rationale}
        label_count = sum(entry["label"] == label for entry in self._entries.values())

        return {"recorded_comment_id": comment_id, "recorded_total": len(self), "label": label, "label_count": label_count}

    def summarize(self, group_by: GroupBy) -> dict[str, object]:
        """Return classification counts and percentages grouped by one field."""
        if not self._entries:
            return {"group_by": group_by, "total_comments": 0, "counts": {}, "percentages": {}}

        counts = Counter(entry[group_by] for entry in self._entries.values())
        total_comments = len(self)

        return {
            "group_by": group_by,
            "total_comments": total_comments,
            "counts": dict(sorted(counts.items())),
            "percentages": {category: round(count / total_comments * 100, 1) for category, count in sorted(counts.items())},
        }


def get_session_ledger(session: AgentSession | None) -> ClassificationLedger:
    """Return the classification ledger owned by the active agent session."""
    if session is None:
        raise RuntimeError("Classification tools require an active agent session")

    ledger = session.state.get(SESSION_LEDGER_KEY)
    if ledger is None:
        ledger = ClassificationLedger()
        session.state[SESSION_LEDGER_KEY] = ledger
    elif not isinstance(ledger, ClassificationLedger):
        raise TypeError(f"Session state key {SESSION_LEDGER_KEY!r} must contain a ClassificationLedger")
    return ledger
