#!/usr/bin/env python3
"""Apply human knowledge validations received over Telegram.

Expert learning jobs run in agent mode: they fetch official sources
deterministically, then the agent writes a *proposal* to
``knowledge/CURRENT.proposed.md`` and delivers a full report plus a validation
request to Telegram. No knowledge is consolidated automatically.

This script closes the loop. It reads Telegram replies from the Hermes state
database, and only from allowed users, applies decisions of the form::

    valide:<profil>     # consolidate proposal into CURRENT.md (backup kept)
    rejette:<profil>    # discard the pending proposal

Aliases are accepted for each profile (e.g. ``valide 3d``). Every processed
message is recorded so a decision is applied exactly once. On first run the
script baselines existing history and acts on nothing, so old unrelated
messages are never replayed.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/opt/data"))
STATE_DB = HERMES_HOME / "state.db"
PROFILES_DIR = HERMES_HOME / "profiles"
INDEX_FILE = HERMES_HOME / "knowledge-validation-tracking.json"
HERMES_BIN = os.environ.get("HERMES_BIN", "/opt/hermes/.venv/bin/hermes")
NOTIFY = os.environ.get("KNOWLEDGE_VALIDATION_NOTIFY", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}

# Profile token -> canonical profile directory name.
PROFILE_ALIASES = {
    "designer-3d-agent": "designer-3d-agent",
    "designer-3d": "designer-3d-agent",
    "designer": "designer-3d-agent",
    "design-3d": "designer-3d-agent",
    "3d": "designer-3d-agent",
    "bureau-etudes-agent": "bureau-etudes-agent",
    "bureau-etudes": "bureau-etudes-agent",
    "bureau": "bureau-etudes-agent",
    "be": "bureau-etudes-agent",
    "structure": "bureau-etudes-agent",
    "calcul": "bureau-etudes-agent",
    "calcul-structure": "bureau-etudes-agent",
    "etudes": "bureau-etudes-agent",
    "community-manager": "community-manager",
    "community": "community-manager",
    "communaute": "community-manager",
    "cm": "community-manager",
}

APPROVE = re.compile(
    r"^\s*(valide[rz]?|valid[eé]e?s?|approuve[rz]?|approve[rd]?)\b[\s:,;.\-]+(.+)$",
    re.I,
)
REJECT = re.compile(
    r"^\s*(rejette[rz]?|rejet(?:te|er)?|refuse[rz]?|reject(?:ed)?)\b[\s:,;.\-]+(.+)$",
    re.I,
)
TOKEN = re.compile(r"[a-z0-9][a-z0-9-]*")


def allowed_users() -> set[str]:
    raw = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
    return {value.strip() for value in raw.split(",") if value.strip()}


def resolve_profile(remainder: str) -> str | None:
    match = TOKEN.search(remainder.lower())
    if not match:
        return None
    return PROFILE_ALIASES.get(match.group(0))


def parse_decision(message: str) -> tuple[str, str] | None:
    text = " ".join(message.split())
    approve = APPROVE.match(text)
    if approve:
        profile = resolve_profile(approve.group(2))
        return ("approve", profile) if profile else None
    reject = REJECT.match(text)
    if reject:
        profile = resolve_profile(reject.group(2))
        return ("reject", profile) if profile else None
    return None


def load_index() -> dict:
    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("version", 1)
            data.setdefault("baselined", False)
            data.setdefault("processed", {})
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"version": 1, "baselined": False, "processed": {}}


def save_index(index: dict) -> None:
    tmp = INDEX_FILE.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(tmp, INDEX_FILE)


def telegram_messages() -> list[sqlite3.Row]:
    connection = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(
            """
            SELECT m.id, m.session_id, m.timestamp, m.content, s.user_id
            FROM messages AS m
            JOIN sessions AS s ON s.id = m.session_id
            WHERE s.source = 'telegram'
              AND m.role = 'user'
              AND coalesce(m.content, '') <> ''
            ORDER BY m.id
            """
        ).fetchall()
    finally:
        connection.close()


def send_telegram(chat_id: str, message: str) -> bool:
    if not NOTIFY:
        return False
    target = f"telegram:{chat_id}" if chat_id else "telegram"
    completed = subprocess.run(
        [HERMES_BIN, "send", "--to", target, "--quiet", message],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "HERMES_HOME": str(HERMES_HOME)},
    )
    return completed.returncode == 0


def apply_decision(action: str, profile: str) -> tuple[str, str]:
    """Return (verdict, human_message). verdict in {applied, rejected, noop, error}."""
    knowledge = PROFILES_DIR / profile / "knowledge"
    proposed = knowledge / "CURRENT.proposed.md"
    current = knowledge / "CURRENT.md"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    if not knowledge.is_dir():
        return "error", f"Profil inconnu ou non initialisé: {profile}"

    if not proposed.is_file():
        return (
            "noop",
            f"Aucune proposition en attente pour {profile}. Rien appliqué.",
        )

    if action == "approve":
        applied_dir = knowledge / "applied"
        applied_dir.mkdir(parents=True, exist_ok=True)
        if current.is_file():
            backup = applied_dir / f"CURRENT-{stamp}.md"
            backup.write_text(current.read_text(encoding="utf-8"), encoding="utf-8")
        current.write_text(proposed.read_text(encoding="utf-8"), encoding="utf-8")
        (applied_dir / f"proposal-{stamp}.md").write_text(
            proposed.read_text(encoding="utf-8"), encoding="utf-8"
        )
        proposed.unlink()
        return (
            "applied",
            f"✅ {profile}: proposition consolidée dans CURRENT.md "
            f"(backup conservé applied/CURRENT-{stamp}.md).",
        )

    rejected_dir = knowledge / "rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    (rejected_dir / f"{stamp}.md").write_text(
        proposed.read_text(encoding="utf-8"), encoding="utf-8"
    )
    proposed.unlink()
    return (
        "rejected",
        f"🚫 {profile}: proposition rejetée et archivée "
        f"(rejected/{stamp}.md). CURRENT.md inchangé.",
    )


def main() -> int:
    if not STATE_DB.exists():
        raise SystemExit(f"Missing Hermes state database: {STATE_DB}")

    users = allowed_users()
    index = load_index()
    processed = index["processed"]
    messages = telegram_messages()

    # First run: baseline existing history so old messages are never replayed.
    if not index["baselined"]:
        for row in messages:
            processed[str(int(row["id"]))] = {"baseline": True}
        index["baselined"] = True
        save_index(index)
        print(json.dumps({"ok": True, "baselined": len(processed)}, ensure_ascii=False))
        return 0

    applied = 0
    for row in messages:
        key = str(int(row["id"]))
        if key in processed:
            continue
        user_id = str(row["user_id"] or "").strip()
        # Only allowed users may mutate validated knowledge.
        if users and user_id not in users:
            processed[key] = {"skipped": "unauthorized"}
            continue
        decision = parse_decision(str(row["content"]))
        if decision is None:
            processed[key] = {"skipped": "no-decision"}
            continue
        action, profile = decision
        verdict, human = apply_decision(action, profile)
        sent = send_telegram(user_id, "Hermes — validation connaissances\n\n" + human)
        processed[key] = {
            "action": action,
            "profile": profile,
            "verdict": verdict,
            "notified": sent,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        save_index(index)
        if verdict in {"applied", "rejected"}:
            applied += 1

    save_index(index)
    print(
        json.dumps(
            {"ok": True, "applied": applied, "processed": len(processed)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 — surface failures to the cron log
        print(f"KNOWLEDGE_VALIDATION_ERROR={type(error).__name__}: {error}", file=sys.stderr)
        raise
