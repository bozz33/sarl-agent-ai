#!/usr/bin/env python3
"""Install deterministic maintenance scripts into Hermes profiles."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTAINER = "sarl-hermes-agent"
PROFILE = "sarl-stack-steward"
PROFILE_ROOT = f"/opt/data/profiles/{PROFILE}"
HERMES = "/opt/hermes/.venv/bin/hermes"
JOB_NAME = "sarl-weekly-stack-audit"
SCRIPT_NAME = "weekly-stack-audit.py"


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def main() -> int:
    scripts_dir = f"{PROFILE_ROOT}/scripts"
    run("docker", "exec", CONTAINER, "mkdir", "-p", scripts_dir)
    run(
        "docker",
        "cp",
        str(ROOT / "scripts" / "hermes-weekly-stack-audit.py"),
        f"{CONTAINER}:{scripts_dir}/{SCRIPT_NAME}",
    )
    run(
        "docker",
        "exec",
        CONTAINER,
        "chown",
        "hermes:hermes",
        f"{scripts_dir}/{SCRIPT_NAME}",
    )
    run(
        "docker",
        "exec",
        CONTAINER,
        "chmod",
        "750",
        f"{scripts_dir}/{SCRIPT_NAME}",
    )

    raw = run(
        "docker",
        "exec",
        CONTAINER,
        "cat",
        f"{PROFILE_ROOT}/cron/jobs.json",
        capture=True,
    )
    jobs = json.loads(raw).get("jobs", [])
    job = next(item for item in jobs if item.get("name") == JOB_NAME)

    run(
        "docker",
        "exec",
        "-u",
        "hermes",
        CONTAINER,
        HERMES,
        "-p",
        PROFILE,
        "cron",
        "edit",
        str(job["id"]),
        "--schedule",
        "0 6 * * 1",
        "--name",
        JOB_NAME,
        "--deliver",
        "telegram",
        "--script",
        SCRIPT_NAME,
        "--no-agent",
        "--clear-skills",
        "--workdir",
        "/workspace",
    )
    print(f"{JOB_NAME}: deterministic no-agent audit installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
