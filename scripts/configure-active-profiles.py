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
    "sarl-personal-assistant",
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

# Agents code connectes aux 4 fournisseurs actifs (Claude OAuth, GPT/Codex,
# DeepSeek, Gemini). OpenRouter et Groq sont retires de la strategie active.
CODE_AGENTS = {
    "code-builder",
    "codex-builder",
    "code-reviewer",
    "code-reviewer-critical",
    "qa-agent",
}

SANDBOX_RUNTIME_IMAGE = "sarl/sandbox-runtime:python3.11-nodejs20-playwright"

DOCKER_TERMINAL_PROFILES = {
    "code-builder",
    "codex-builder",
    "qa-agent",
}

# Toolsets sans valeur fonctionnelle ici, desactives pour reduire surface et cout.
# Aucun controle d'ordinateur (computer_use) pour les agents SARL.
DISABLED_TOOLSETS = [
    "computer_use",
    "image_gen",
    "vision_analyze",
    "tts",
    "homeassistant",
    "spotify",
    "messaging",
    "social",
    "social_posting",
    "email_send",
]

# Profils a surface d'outils reduite (agents code + assistant personnel).
TOOLSET_RESTRICTED = CODE_AGENTS | {"sarl-personal-assistant"}


def desired(config: dict, profile_name: str) -> dict:
    config.pop("provider", None)
    config.pop("base_url", None)
    config.pop("openrouter", None)
    config.pop("groq", None)
    config.setdefault("checkpoints", {})["enabled"] = True
    # Verrou natif d'auto-amelioration: toute ecriture de skill par un agent est
    # mise en attente (~/.hermes/pending/skills/) et promue via /skills approve.
    # L'apprentissage (memoire, propositions) reste libre; seule la skill ACTIVE
    # exige validation. memory.write_approval reste false (faits non sensibles).
    config.setdefault("skills", {})["write_approval"] = True
    config["hooks"] = {"pre_tool_call": [HOOK.copy()]}
    config.setdefault("mcp_servers", {})["sarl_project_memory"] = MCP.copy()
    # Groq/OpenRouter retires de la strategie active: ne plus les injecter et
    # les purger s'ils restent.
    config.get("providers", {}).pop("groq", None)
    config.get("providers", {}).pop("openrouter", None)
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

    # Agents code: modele primaire par role + chaine de graduation 4 fournisseurs.
    # La graduation effective (escalade d'une sous-tache difficile vers un palier
    # superieur) passe par delegate_task et le routage orchestrateur.
    if profile_name == "code-builder":
        config.setdefault("model", {}).update(
            {"provider": "deepseek", "default": "deepseek-chat"}
        )
        fallbacks[:] = [
            {"provider": "deepseek", "model": "deepseek-reasoner"},
            {"provider": "anthropic", "model": "claude-sonnet-4.6"},
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "gemini", "model": "gemini-2.5-flash"},
        ]

    if profile_name == "codex-builder":
        config.setdefault("model", {}).update(
            {"provider": "openai-codex", "default": "gpt-5.1-codex-mini"}
        )
        fallbacks[:] = [
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "anthropic", "model": "claude-sonnet-4.6"},
            {"provider": "deepseek", "model": "deepseek-reasoner"},
        ]

    if profile_name == "code-reviewer":
        config.setdefault("model", {}).update(
            {"provider": "deepseek", "default": "deepseek-reasoner"}
        )
        fallbacks[:] = [
            {"provider": "anthropic", "model": "claude-sonnet-4.6"},
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "deepseek", "model": "deepseek-chat"},
        ]

    if profile_name == "code-reviewer-critical":
        config.setdefault("model", {}).update(
            {"provider": "anthropic", "default": "claude-sonnet-4.6"}
        )
        fallbacks[:] = [
            {"provider": "openai-api", "model": "gpt-4.1"},
            {"provider": "deepseek", "model": "deepseek-reasoner"},
        ]

    if profile_name == "qa-agent":
        config.setdefault("model", {}).update(
            {"provider": "gemini", "default": "gemini-2.5-flash"}
        )
        fallbacks[:] = [
            {"provider": "deepseek", "model": "deepseek-chat"},
            {"provider": "anthropic", "model": "claude-sonnet-4.6"},
        ]

    # Assistant personnel: modele economique en lecture/synthese, fallback deepseek.
    # Role lecture seule + brouillons; tout envoi reste soumis a validation humaine.
    if profile_name == "sarl-personal-assistant":
        config.setdefault("model", {}).update(
            {"provider": "gemini", "default": "gemini-2.5-flash", "max_tokens": 8192}
        )
        config.setdefault("agent", {}).update({"max_turns": 16, "api_max_retries": 2})
        fallbacks[:] = [{"provider": "deepseek", "model": "deepseek-chat"}]

    if profile_name in TOOLSET_RESTRICTED:
        config.setdefault("agent", {})["disabled_toolsets"] = list(DISABLED_TOOLSETS)

    if profile_name in DOCKER_TERMINAL_PROFILES:
        terminal = config.setdefault("terminal", {})
        terminal["backend"] = "docker"
        terminal["docker_image"] = SANDBOX_RUNTIME_IMAGE
        terminal["singularity_image"] = f"docker://{SANDBOX_RUNTIME_IMAGE}"
        terminal["modal_image"] = SANDBOX_RUNTIME_IMAGE
        terminal["daytona_image"] = SANDBOX_RUNTIME_IMAGE
        terminal["docker_run_as_host_user"] = True

    # Resilience: si DeepSeek est epuise/indisponible (quota, panne API), basculer
    # sur Claude -> GPT -> Gemini. Les agents code ont deja une chaine dediee.
    if (
        config.get("model", {}).get("provider") == "deepseek"
        and profile_name not in CODE_AGENTS
    ):
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
