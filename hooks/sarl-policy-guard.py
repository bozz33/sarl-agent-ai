#!/usr/bin/env python3
"""Hermes pre_tool_call guard for SARL-Agent-AI.

Reads one Hermes shell-hook JSON payload from stdin. Emits a block directive
for high-risk commands and writes a redacted JSONL audit event when a log path
is configured.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("recursive-delete", re.compile(r"(^|[;&|]\s*)rm\s+[^;\n]*(?:-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b", re.I)),
    ("docker-compose-down", re.compile(r"\bdocker\s+compose\s+down\b", re.I)),
    ("docker-compose-pull", re.compile(r"\bdocker\s+compose\s+pull\b", re.I)),
    ("docker-compose-up", re.compile(r"\bdocker\s+compose\s+up\b", re.I)),
    ("system-service-change", re.compile(r"\bsystemctl\s+(?:stop|restart|disable|mask)\b", re.I)),
    ("firewall-disable", re.compile(r"\bufw\s+disable\b|\b(?:iptables|nft)\s+-F\b", re.I)),
    ("database-destructive", re.compile(r"\b(?:DROP\s+(?:DATABASE|TABLE|SCHEMA)|TRUNCATE(?:\s+TABLE)?|ALTER\s+TABLE)\b", re.I)),
    ("world-writable", re.compile(r"\bchmod\s+(?:-R\s+)?777\b", re.I)),
    ("root-recursive-chown", re.compile(r"\bchown\s+-R\b[^;\n]*\s/(?:\s|$)", re.I)),
    ("public-listener", re.compile(r"(?:0\.0\.0\.0|\[::\])(?::\d+)?", re.I)),
    ("webserver-config", re.compile(r"(?:/etc/(?:nginx|apache2|caddy)|\b(?:nginx|apache2|caddy)\s+(?:reload|restart))", re.I)),
    ("dns-change", re.compile(r"\b(?:cloudflare|route53|dns)\b[^;\n]*(?:update|delete|create|change)", re.I)),
)

SENSITIVE_PATH = re.compile(
    r"(^|[\s'\"=:/])(?:\.env(?:\.[^\s/'\"]+)?|\.secrets|secrets)(?:[/\s'\";]|$)",
    re.I,
)
SAFE_NEGATIVE_PATH_PROBE = re.compile(
    r"""^\s*(?:
        test\s+!\s+-(?:e|f|d|r|w|x)\s+\S+
        |
        \[\s+!\s+-(?:e|f|d|r|w|x)\s+\S+\s+\]
    )\s*$""",
    re.I | re.X,
)
WRITE_TOOLS = frozenset({"write_file", "patch", "terminal", "execute_code"})
MAX_LOG_COMMAND = 500


def _extract_text(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    fields: list[str] = []
    for key in ("command", "cmd", "path", "file_path", "patch", "content"):
        value = tool_input.get(key)
        if isinstance(value, str):
            fields.append(value)
    return "\n".join(fields)


def _has_unsafe_sensitive_reference(tool_name: str, text: str) -> bool:
    if not SENSITIVE_PATH.search(text):
        return False
    if tool_name not in {"terminal", "execute_code"}:
        return True

    # Negative metadata probes prove that a secret path is not exposed without
    # reading or changing it. Every other sensitive-path reference is blocked.
    segments = re.split(r"(?:&&|\|\||[;\n])", text)
    sensitive_segments = [
        segment.strip() for segment in segments if SENSITIVE_PATH.search(segment)
    ]
    return not sensitive_segments or any(
        not SAFE_NEGATIVE_PATH_PROBE.fullmatch(segment)
        for segment in sensitive_segments
    )


def evaluate(payload: dict[str, Any]) -> tuple[bool, str, str]:
    tool_name = str(payload.get("tool_name") or "")
    text = _extract_text(payload)

    if tool_name not in WRITE_TOOLS:
        return False, "", ""

    if _has_unsafe_sensitive_reference(tool_name, text):
        return True, "sensitive-path", "Modification de .env/.secrets bloquee; validation humaine requise."

    for rule_id, pattern in RULES:
        if pattern.search(text):
            return True, rule_id, f"Action critique bloquee par sarl-policy-guard ({rule_id}); validation humaine requise."

    return False, "", ""


def _redact(value: str) -> str:
    value = re.sub(
        r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*\S+",
        r"\1=REDACTED",
        value,
    )
    value = re.sub(r"\bsk-(?:or-)?[A-Za-z0-9_-]{8,}\b", "REDACTED", value)
    return value[:MAX_LOG_COMMAND]


def audit(payload: dict[str, Any], blocked: bool, rule_id: str) -> None:
    log_path = os.environ.get(
        "SARL_POLICY_GUARD_LOG",
        "/opt/data/logs/sarl-policy-guard.log",
    )
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "blocked": blocked,
        "rule": rule_id or None,
        "tool_name": payload.get("tool_name"),
        "session_id": payload.get("session_id") or "",
        "cwd": payload.get("cwd") or "",
        "input": _redact(_extract_text(payload)),
    }
    try:
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        print(
            json.dumps(
                {
                    "action": "block",
                    "message": "Payload hook invalide; blocage par securite.",
                }
            )
        )
        return 0

    if not isinstance(payload, dict):
        print(
            json.dumps(
                {
                    "action": "block",
                    "message": "Payload hook invalide; blocage par securite.",
                }
            )
        )
        return 0

    blocked, rule_id, message = evaluate(payload)
    audit(payload, blocked, rule_id)
    if blocked:
        print(json.dumps({"action": "block", "message": message}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
