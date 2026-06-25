# SARL social wrappers — specification

Status: design only. No execution. Read-only first, drafts next, publish only
after explicit human validation.

## Rationale

Generic multi-social MCP servers expose broad permissions (publish, schedule,
delete, reply across platforms). SARL exposes a narrow, named wrapper surface per
platform instead, mapped onto official APIs, so every tool name is controlled and
every outbound action is gated.

X already ships through the bundled `xurl` skill (read-only usage first). LinkedIn,
Meta (Facebook/Instagram) and others require SARL wrappers built on their official
APIs.

## Tool surface (per platform)

Read-only (safe, default):

```text
social_list_notifications    # new notifications/mentions
social_list_comments         # comments on owned pages/posts
social_get_message_summary   # summarize a thread/DM without exposing secrets
```

Draft (prepared, never sent):

```text
social_prepare_reply         # draft reply, returns proposal record
social_prepare_post          # draft post, returns proposal record
```

Gated (human validation required):

```text
social_publish_after_approval   # publish only after explicit greenlight
```

## Phases

1. Read-only: notifications, comments, message summaries. No write scope requested.
2. Drafts: prepare replies and posts as proposals. No publish scope.
3. Publish after approval: single gated tool, one item at a time, with the
   validation record below.

## Validation record (every outbound action)

```text
ACTION_PROPOSED:
ACCOUNT:
COMPANY/PROJECT:
RISK:
CONTENT:
HUMAN_VALIDATION_REQUIRED: yes
```

## Classification

Every ingested item is normalized via the `sarl-source-classification` skill before
triage. Items with `company_id = unknown` or `project_id = unknown` are not
dispatched automatically.

## Security

- Minimal OAuth scopes; request write scopes only at the phase that needs them.
- No tokens or secrets in memory, skills, logs, Telegram, or reports.
- Per-platform, per-account isolation; never a single broad credential.
- Tool allowlist enforced; publish/delete tools disabled until phase 3.

## Per-platform official API references

- LinkedIn: Community Management / Comments API (create, edit, delete per scope).
- Meta (Instagram/Facebook): publish media, manage and reply to comments per
  granted permissions.
- X: search, fetch and post; direct messages per access tier and plan.
