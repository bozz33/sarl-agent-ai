#!/usr/bin/env python3
"""Apply the common SARL safety and memory baseline to active Hermes profiles."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


PROFILES = (
    "sarl-router",
    "sarl-orchestrator",
    "sarl-orchestrator-critical",
    "research-sage",
    "docs-scribe",
    "sarl-governor",
    "sarl-stack-steward",
    "code-builder",
    "codex-builder",
    "code-reviewer",
    "code-reviewer-critical",
    "qa-agent",
    "ops-foundation",
    "cpanel-watch-agent",
    "security-audit-agent",
    "community-manager",
    "support-agent",
    "bureau-etudes-agent",
    "designer-3d-agent",
)

HOOK = {
    "matcher": "terminal|execute_code|write_file|patch",
    "command": "/opt/sarl-hooks/sarl-policy-guard.py",
    "timeout": 5,
}

MCP = {
    "url": "http://project-memory-mcp:8000/mcp",
    "enabled": True,
}

GROQ_PROVIDER = {
    "name": "Groq",
    "api": "https://api.groq.com/openai/v1",
    "key_env": "GROQ_API_KEY",
    "transport": "chat_completions",
    "default_model": "llama-3.3-70b-versatile",
    "models": {
        "llama-3.3-70b-versatile": {
            "context_length": 131072,
        },
        "qwen/qwen3-32b": {
            "context_length": 131072,
        },
    },
    "discover_models": True,
}

OPENAI_PROVIDER = {
    "name": "OpenAI API",
    "api": "https://api.openai.com/v1",
    "key_env": "OPENAI_API_KEY",
    "api_mode": "chat_completions",
    "transport": "chat_completions",
    "default_model": "gpt-4.1-mini",
    "models": {
        "gpt-4.1-mini": {
            "context_length": 1047576,
        },
    },
    "discover_models": True,
}


def desired(config: dict, profile_name: str) -> dict:
    config.pop("provider", None)
    config.pop("base_url", None)
    config.setdefault("checkpoints", {})["enabled"] = True
    config["hooks"] = {"pre_tool_call": [HOOK.copy()]}
    config.setdefault("mcp_servers", {})["sarl_project_memory"] = MCP.copy()
    config.setdefault("providers", {})["groq"] = GROQ_PROVIDER.copy()
    config.setdefault("providers", {})["openai-api"] = OPENAI_PROVIDER.copy()
    config.setdefault("web", {})["search_backend"] = "ddgs"

    fallbacks = config.setdefault("fallback_providers", [])
    fallbacks[:] = [
        item
        for item in fallbacks
        if item.get("provider") not in {"groq", "openrouter"}
    ]

    if profile_name == "sarl-orchestrator":
        # Cerveau central: modele de raisonnement par abonnement (Claude Sonnet
        # via OAuth), jamais economique. Fallback GPT puis Gemini.
        config.setdefault("model", {}).update(
            {
                "provider": "anthropic",
                "default": "claude-sonnet-4.6",
            }
        )
        fallbacks[:] = [
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "gemini", "model": "gemini-2.5-flash"},
        ]

    if profile_name in {"cpanel-watch-agent", "security-audit-agent"}:
        # Watchers lecture seule: modele economique deepseek, fallback gemini.
        config.setdefault("model", {}).update(
            {
                "provider": "deepseek",
                "default": "deepseek-chat",
            }
        )
        fallbacks[:] = [{"provider": "gemini", "model": "gemini-2.5-flash"}]

    if profile_name == "sarl-stack-steward":
        config.setdefault("model", {}).update(
            {
                "provider": "deepseek",
                "default": "deepseek-chat",
                "max_tokens": 8192,
            }
        )
        config.setdefault("agent", {}).update(
            {
                "max_turns": 20,
                "api_max_retries": 2,
            }
        )
        fallbacks.clear()

    if profile_name in {"designer-3d-agent", "community-manager"}:
        config.setdefault("model", {}).update(
            {
                "provider": "gemini",
                "default": "gemini-3.1-flash-lite",
                "max_tokens": 8192,
            }
        )
        config.setdefault("agent", {}).update(
            {
                "max_turns": 12,
                "api_max_retries": 2,
            }
        )
        fallbacks[:] = [{"provider": "deepseek", "model": "deepseek-chat"}]

    if profile_name == "bureau-etudes-agent":
        config.setdefault("model", {}).update(
            {
                "provider": "deepseek",
                "default": "deepseek-reasoner",
                "max_tokens": 8192,
            }
        )
        config.setdefault("agent", {}).update(
            {
                "max_turns": 16,
                "api_max_retries": 2,
                "reasoning_effort": "medium",
            }
        )
        fallbacks[:] = [{"provider": "gemini", "model": "gemini-2.5-flash"}]

    # Resilience: si DeepSeek est epuise/indisponible (quota, panne API), basculer
    # sur Claude -> GPT -> Gemini.
    if config.get("model", {}).get("provider") == "deepseek":
        fallbacks[:] = [
            {"provider": "anthropic", "model": "claude-sonnet-4.6"},
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "gemini", "model": "gemini-2.5-flash"},
        ]

    # Toute decomposition/dispatch Kanban passe par l'orchestrateur central.
    config.setdefault("kanban", {})["orchestrator_profile"] = "sarl-orchestrator"

    for auxiliary in config.get("auxiliary", {}).values():
        if isinstance(auxiliary, dict) and auxiliary.get("provider") in {
            "groq",
            "openrouter",
        }:
            auxiliary["provider"] = "deepseek"
            auxiliary["model"] = "deepseek-chat"

    smart_routing = config.get("smart_model_routing", {})
    if str(smart_routing.get("cheap_model", "")).startswith("groq/"):
        smart_routing["cheap_model"] = "deepseek/deepseek-chat"

    return config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("/opt/data/profiles"),
        help="Hermes profiles directory",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed: list[str] = []
    missing: list[str] = []

    paths = [args.root.parent / "config.yaml"]
    paths.extend(args.root / name / "config.yaml" for name in PROFILES)

    for path in paths:
        if not path.is_file():
            missing.append(str(path))
            continue
        before = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        profile_name = (
            "default" if path == args.root.parent / "config.yaml" else path.parent.name
        )
        after = desired(before.copy(), profile_name)
        rendered = yaml.safe_dump(after, sort_keys=False, allow_unicode=True)
        if path.read_text(encoding="utf-8") != rendered:
            changed.append("default" if path == args.root.parent / "config.yaml" else path.parent.name)
            if not args.check:
                path.write_text(rendered, encoding="utf-8")

    if missing:
        print("Missing profiles: " + ", ".join(missing))
        return 1
    if args.check and changed:
        print("Profiles outside baseline: " + ", ".join(changed))
        return 1

    action = "Would update" if args.check else "Updated"
    print(f"{action} {len(changed)} profile(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
