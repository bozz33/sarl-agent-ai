#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 /absolute/project/path agent-id branch-name" >&2
  exit 2
}

PROJECT_ROOT="${1:-}"
AGENT_ID="${2:-}"
BRANCH="${3:-}"

[[ -n "$PROJECT_ROOT" && -n "$AGENT_ID" && -n "$BRANCH" ]] || usage
[[ "$PROJECT_ROOT" == /root/CascadeProjects/SARL-agent-ai/projects/* ]] || {
  echo "Project must be under official projects root." >&2
  exit 1
}
[[ "$AGENT_ID" =~ ^[a-z0-9][a-z0-9_-]{0,63}$ ]] || {
  echo "Invalid agent id." >&2
  exit 1
}
[[ "$BRANCH" =~ ^[A-Za-z0-9._/-]+$ ]] || {
  echo "Invalid branch name." >&2
  exit 1
}

SOURCE="$PROJECT_ROOT/source"
WORKTREE="$PROJECT_ROOT/worktrees/$AGENT_ID"

[[ -d "$SOURCE/.git" || -f "$SOURCE/.git" ]] || {
  echo "Missing Git repository: $SOURCE" >&2
  exit 1
}
[[ ! -e "$WORKTREE" ]] || {
  echo "Worktree path already exists: $WORKTREE" >&2
  exit 1
}

mkdir -p "$PROJECT_ROOT/worktrees"

if git -C "$SOURCE" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git -C "$SOURCE" worktree add "$WORKTREE" "$BRANCH"
else
  git -C "$SOURCE" worktree add -b "$BRANCH" "$WORKTREE"
fi

git -C "$SOURCE" worktree list --porcelain
