#!/usr/bin/env python3
"""Make premium-target profiles safe to select before premium auth is available."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path("/opt/data/profiles")
HOOK = {
    "matcher": "terminal|execute_code|write_file|patch",
    "command": "/opt/sarl-hooks/sarl-policy-guard.py",
    "timeout": 5,
}
MCP = {
    "sarl_project_memory": {
        "url": "http://project-memory-mcp:8000/mcp",
        "enabled": True,
    }
}


def configure(target: str, template: str, docker_backend: bool) -> None:
    template_config = yaml.safe_load(
        (ROOT / template / "config.yaml").read_text(encoding="utf-8")
    )
    config = deepcopy(template_config)
    config["model"] = {
        "provider": "deepseek",
        "default": "deepseek-reasoner",
    }
    config["fallback_providers"] = [
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openrouter", "model": "auto"},
    ]
    config.pop("provider", None)
    config.pop("base_url", None)
    config.setdefault("checkpoints", {})["enabled"] = True
    config["hooks"] = {"pre_tool_call": [HOOK.copy()]}
    config["mcp_servers"] = deepcopy(MCP)
    config.setdefault("agent", {})["api_max_retries"] = 1
    config["agent"]["gateway_timeout"] = 600
    config["agent"]["gateway_timeout_warning"] = 120
    if docker_backend:
        config.setdefault("terminal", {})["backend"] = "docker"
        config["terminal"]["docker_image"] = (
            "sha256:d14ae8d7fcee933e82c9f62eded621110f227bc96363ca5449d36897af7bea1c"
        )
        config["terminal"]["docker_run_as_host_user"] = True
    else:
        config.setdefault("terminal", {})["backend"] = "local"

    path = ROOT / target / "config.yaml"
    path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


configure("codex-builder", "code-builder", docker_backend=True)
configure("code-reviewer-critical", "code-reviewer", docker_backend=False)
print("Configured provisional premium profiles")
