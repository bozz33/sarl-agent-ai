#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d /root/CascadeProjects/SARL-agent-ai/projects/.worktree-test.XXXXXX)"
SOURCE="$ROOT/source"

cleanup() {
  if [[ -d "$SOURCE/.git" ]]; then
    git -C "$SOURCE" worktree remove --force "$ROOT/worktrees/code-builder" \
      >/dev/null 2>&1 || true
  fi
  rm -rf "$ROOT"
}
trap cleanup EXIT

mkdir -p "$SOURCE"
git -C "$SOURCE" init -q
git -C "$SOURCE" config user.name "SARL Test"
git -C "$SOURCE" config user.email "test@localhost"
echo "proof" > "$SOURCE/README.md"
git -C "$SOURCE" add README.md
git -C "$SOURCE" commit -qm "test fixture"

"$(dirname "$0")/create-worktree.sh" \
  "$ROOT" \
  code-builder \
  "agent/code-builder-test" >/dev/null

test -f "$ROOT/worktrees/code-builder/README.md"
test "$(git -C "$ROOT/worktrees/code-builder" branch --show-current)" \
  = "agent/code-builder-test"

echo "WORKTREE_TEST_OK"
