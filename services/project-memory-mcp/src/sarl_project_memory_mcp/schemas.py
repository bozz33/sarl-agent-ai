from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


MEMORY_TYPES = frozenset(
    {
        "fact",
        "hypothesis",
        "decision",
        "constraint",
        "preference",
        "technical_note",
        "incident",
        "solution",
        "risk",
        "meeting_summary",
        "task_summary",
        "handoff",
        "report",
        "deprecated",
        "superseded",
    }
)

TRUTH_STATUSES = frozenset(
    {"hypothesis", "confirmed", "decision", "deprecated", "superseded"}
)


class MemoryValidationError(ValueError):
    """Raised when a memory request violates the SARL memory policy."""


@dataclass(frozen=True)
class MemoryWrite:
    project_id: str
    type: str
    content: str
    truth_status: str
    source_type: str | None = None
    source_path: str | None = None
    source_url: str | None = None
    created_by_profile: str | None = None
    validated_by: str | None = None
    confidence: Decimal = Decimal("0.70")
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None
    supersedes_id: str | None = None
