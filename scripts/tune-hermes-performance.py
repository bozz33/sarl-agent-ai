#!/usr/bin/env python3
"""Tune Hermes profiles for responsive interactive use without reducing safeguards."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path("/opt/data")
FAST_MODEL = {"provider": "gemini", "default": "gemini-3.1-flash-lite"}
FAST_FALLBACKS = [
    {"provider": "deepseek", "model": "deepseek-chat"},
    {"provider": "openrouter", "model": "auto"},
]

FAST_PROFILES = {
    "sarl-router",
    "research-sage",
    "docs-scribe",
    "sarl-stack-steward",
    "qa-agent",
    "ops-foundation",
    "community-manager",
    "support-agent",
    "designer-3d-agent",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save(path: Path, config: dict) -> None:
    path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def tune_agent(config: dict, fast: bool) -> None:
    config.pop("provider", None)
    config.pop("base_url", None)
    agent = config.setdefault("agent", {})
    agent["api_max_retries"] = 1
    agent["gateway_timeout"] = 600
    agent["gateway_timeout_warning"] = 120
    if fast:
        agent["reasoning_effort"] = "low"
        agent["environment_probe"] = False
        agent["coding_context"] = "off"
        agent["max_turns"] = min(int(agent.get("max_turns", 60)), 30)
    config.setdefault("prompt_caching", {})["cache_ttl"] = "1h"
    config.setdefault("openrouter", {})["response_cache"] = True
    config["openrouter"]["response_cache_ttl"] = 3600
    config.setdefault("provider_routing", {})["sort"] = "throughput"


default_path = ROOT / "config.yaml"
default = load(default_path)
default["model"] = FAST_MODEL.copy()
default["fallback_providers"] = [item.copy() for item in FAST_FALLBACKS]
tune_agent(default, fast=True)
save(default_path, default)

for profile_dir in sorted((ROOT / "profiles").iterdir()):
    path = profile_dir / "config.yaml"
    if not path.is_file():
        continue
    name = profile_dir.name
    config = load(path)
    fast = name in FAST_PROFILES
    if fast:
        config["model"] = FAST_MODEL.copy()
        config["fallback_providers"] = [
            item.copy() for item in FAST_FALLBACKS
        ]
    tune_agent(config, fast=fast)
    if name == "sarl-router":
        config["agent"]["reasoning_effort"] = "medium"
    save(path, config)

print("Hermes performance tuning applied")
