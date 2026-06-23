from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import PurePath
from typing import Any, Iterable

from .schemas import MEMORY_TYPES, TRUTH_STATUSES, MemoryValidationError, MemoryWrite


_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*\S+", re.I),
    re.compile(r"\bsk-(?:or-)?[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
)

_SECRET_PATH_PARTS = frozenset(
    {".env", ".secrets", "secrets", "credentials", "private_keys"}
)


def normalize_allowed_projects(value: str | Iterable[str]) -> frozenset[str]:
    raw = value.split(",") if isinstance(value, str) else value
    projects = frozenset(item.strip() for item in raw if item and item.strip())
    if not projects:
        raise MemoryValidationError("SARL_MEMORY_ALLOWED_PROJECTS must not be empty")
    return projects


def validate_project(project_id: str, allowed_projects: frozenset[str]) -> str:
    project_id = project_id.strip()
    if not project_id:
        raise MemoryValidationError("project_id is required")
    if project_id not in allowed_projects:
        raise MemoryValidationError(f"project_id not allowed: {project_id}")
    return project_id


def reject_secrets(content: str, source_path: str | None = None) -> None:
    for pattern in _SECRET_PATTERNS:
        if pattern.search(content):
            raise MemoryValidationError("content resembles a secret and cannot be stored")
    if source_path:
        parts = {part.lower() for part in PurePath(source_path).parts}
        if parts & _SECRET_PATH_PARTS:
            raise MemoryValidationError("secret-bearing source paths cannot be indexed")


def normalize_confidence(value: float | str | Decimal) -> Decimal:
    try:
        confidence = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise MemoryValidationError("confidence must be numeric") from exc
    if confidence < 0 or confidence > 1:
        raise MemoryValidationError("confidence must be between 0 and 1")
    return confidence


def validate_memory_write(
    *,
    allowed_projects: frozenset[str],
    project_id: str,
    type: str,
    content: str,
    truth_status: str,
    source_type: str | None = None,
    source_path: str | None = None,
    source_url: str | None = None,
    created_by_profile: str | None = None,
    validated_by: str | None = None,
    confidence: float | str | Decimal = Decimal("0.70"),
    tags: Iterable[str] | None = None,
    metadata: dict[str, Any] | None = None,
    supersedes_id: str | None = None,
) -> MemoryWrite:
    project_id = validate_project(project_id, allowed_projects)
    memory_type = type.strip()
    status = truth_status.strip()
    text = content.strip()

    if memory_type not in MEMORY_TYPES:
        raise MemoryValidationError(f"unsupported memory type: {memory_type}")
    if status not in TRUTH_STATUSES:
        raise MemoryValidationError(f"unsupported truth_status: {status}")
    if not text:
        raise MemoryValidationError("content is required")
    if len(text) > 100_000:
        raise MemoryValidationError("content exceeds 100000 characters; store large files on disk")
    if memory_type == "decision" and status != "decision":
        raise MemoryValidationError("decision memories require truth_status=decision")
    if memory_type == "hypothesis" and status != "hypothesis":
        raise MemoryValidationError("hypothesis memories require truth_status=hypothesis")

    reject_secrets(text, source_path)
    clean_tags = tuple(sorted({tag.strip() for tag in tags or () if tag.strip()}))
    if len(clean_tags) > 50:
        raise MemoryValidationError("at most 50 tags are allowed")

    return MemoryWrite(
        project_id=project_id,
        type=memory_type,
        content=text,
        truth_status=status,
        source_type=source_type,
        source_path=source_path,
        source_url=source_url,
        created_by_profile=created_by_profile,
        validated_by=validated_by,
        confidence=normalize_confidence(confidence),
        tags=clean_tags,
        metadata=metadata or {},
        supersedes_id=supersedes_id,
    )
