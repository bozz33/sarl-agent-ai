#!/usr/bin/env python3
"""Create a Gmail draft. Never sends.

Phase 2 wrapper for the sarl-personal-assistant profile. It creates a draft with
the gmail.compose scope and stops there: sending stays a separate, human-validated
action (greenlightRequiredFor: send-email). The draft is visible in the owner's
Gmail Drafts folder for review.

Reads the profile-scoped OAuth token written by the google-workspace skill at
$HERMES_HOME/google_token.json. Run inside the agent container as the profile user.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = os.path.join(
    os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")),
    "google_token.json",
)


def _credentials() -> Credentials:
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w", encoding="utf-8") as handle:
            handle.write(creds.to_json())
    return creds


def create_draft(to: str, subject: str, body: str, cc: str | None) -> dict:
    message = EmailMessage()
    message["To"] = to
    if cc:
        message["Cc"] = cc
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service = build("gmail", "v1", credentials=_credentials(), cache_discovery=False)
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw}})
        .execute()
    )
    return {
        "draft_id": draft.get("id"),
        "message_id": draft.get("message", {}).get("id"),
        "status": "draft_created_not_sent",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--cc")
    args = parser.parse_args()
    print(json.dumps(create_draft(args.to, args.subject, args.body, args.cc), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
