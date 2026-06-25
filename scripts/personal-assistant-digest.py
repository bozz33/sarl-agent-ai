#!/usr/bin/env python3
"""Read-only personal digest: unread email and upcoming calendar events.

Deterministic collector for the sarl-personal-assistant profile. It only reads
through the google-workspace API wrapper (no send, no modify, no delete) and
returns a compact digest for the owner. Deeper triage and company/project
classification are left to the agent via the sarl-source-classification skill.

Runs inside the agent container with the profile-scoped Hermes home, for example:

    docker exec -u hermes \\
      -e HOME=/opt/data/profiles/sarl-personal-assistant \\
      -e HERMES_HOME=/opt/data/profiles/sarl-personal-assistant \\
      sarl-hermes-agent python /opt/sarl-maintenance/personal-assistant-digest.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

GOOGLE_API = os.environ.get(
    "GOOGLE_API_SCRIPT",
    "/opt/hermes/skills/productivity/google-workspace/scripts/google_api.py",
)


def _run(args: list[str]) -> list[dict]:
    result = subprocess.run(
        ["python", GOOGLE_API, *args],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(result.stdout or "[]")
    return data if isinstance(data, list) else [data]


def _truncate(value: str, length: int = 120) -> str:
    value = " ".join((value or "").split())
    return value if len(value) <= length else value[: length - 1] + "…"


def unread_email(max_items: int) -> list[dict]:
    messages = _run(["gmail", "search", "is:unread", "--max", str(max_items)])
    return [
        {
            "source_type": "email",
            "from": _truncate(m.get("from", ""), 80),
            "subject": _truncate(m.get("subject", "(no subject)"), 120),
            "date": m.get("date", ""),
        }
        for m in messages
    ]


def upcoming_events(days: int, max_items: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    events = _run(
        [
            "calendar",
            "list",
            "--start",
            now.isoformat(),
            "--end",
            end.isoformat(),
            "--max",
            str(max_items),
        ]
    )
    return [
        {
            "source_type": "calendar",
            "summary": _truncate(e.get("summary", "(no title)"), 100),
            "start": e.get("start", ""),
        }
        for e in events
    ]


def render_text(digest: dict) -> str:
    lines = [f"Digest assistant - {digest['generated_at']}"]
    emails = digest["email_unread"]
    lines.append(f"\nEmails non lus: {len(emails)}")
    for m in emails:
        lines.append(f"- {m['from']} | {m['subject']}")
    events = digest["calendar_upcoming"]
    lines.append(f"\nAgenda a venir: {len(events)}")
    for e in events:
        lines.append(f"- {e['start']} | {e['summary']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-email", type=int, default=15)
    parser.add_argument("--max-events", type=int, default=15)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--text", action="store_true", help="Human-readable digest")
    args = parser.parse_args()

    digest = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "email_unread": unread_email(args.max_email),
        "calendar_upcoming": upcoming_events(args.days, args.max_events),
    }

    print(render_text(digest) if args.text else json.dumps(digest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
