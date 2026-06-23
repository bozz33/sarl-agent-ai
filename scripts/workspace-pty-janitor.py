#!/usr/bin/env python3
"""Remove duplicate Workspace log-tail PTYs while preserving the newest viewer."""

from __future__ import annotations

import os
import signal
from collections import defaultdict
from pathlib import Path


def cmdline(pid: int) -> list[str]:
    try:
        raw = (Path("/proc") / str(pid) / "cmdline").read_bytes()
    except OSError:
        return []
    return [part.decode("utf-8", "replace") for part in raw.split(b"\0") if part]


groups: dict[str, list[int]] = defaultdict(list)
for entry in Path("/proc").iterdir():
    if not entry.name.isdigit():
        continue
    pid = int(entry.name)
    args = cmdline(pid)
    if "pty-helper.py" not in " ".join(args):
        continue
    if "tail" not in args or "-F" not in args:
        continue
    try:
        log_path = args[args.index("-F") + 1]
    except (ValueError, IndexError):
        continue
    groups[log_path].append(pid)

killed = 0
duplicates = 0
for log_path, pids in groups.items():
    if len(pids) <= 1:
        continue
    duplicates += len(pids) - 1
    for pid in sorted(pids)[:-1]:
        try:
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except ProcessLookupError:
            pass

print(
    f"workspace_pty_groups={len(groups)} "
    f"duplicates={duplicates} terminated={killed}"
)
