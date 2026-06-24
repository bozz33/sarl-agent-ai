#!/usr/bin/env python3
"""Collecte deterministe de l'usage modeles pour l'audit de cout mensuel.

Porte par le cron `monthly-model-cost-audit` du profil sarl-orchestrator (toute
mission entre par l'orchestrateur central). Le script appelle `hermes insights`
(global + par profil actif) en lecture seule et ecrit un rapport date que
l'orchestrateur analyse ensuite pour detecter les derives de cout (usage premium
non justifie, Opus/Codex automatiques, modeles obsoletes).

Robuste: toute exception est capturee, verdict SUPERVISION_REQUISE imprime, code
de sortie 0 pour ne pas casser le tick cron.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


HERMES = "/opt/hermes/.venv/bin/hermes"
DAYS = "30"

# Profils dont l'attribution de cout est la plus utile.
KEY_PROFILES = (
    "sarl-orchestrator",
    "sarl-router",
    "code-builder",
    "codex-builder",
    "code-reviewer-critical",
    "ops-foundation",
    "cpanel-watch-agent",
    "sarl-governor",
    "sarl-stack-steward",
)


def profile_root() -> Path:
    # /opt/data/profiles/<profile>/scripts/model-cost-audit-collect.py
    return Path(__file__).resolve().parent.parent


def insights(*args: str) -> str:
    try:
        result = subprocess.run(
            [HERMES, *args, "insights", "--days", DAYS],
            text=True,
            capture_output=True,
            timeout=120,
        )
        out = (result.stdout or "").strip()
        return out or (result.stderr or "").strip() or "(aucune donnee)"
    except Exception as error:  # noqa: BLE001
        return f"(echec insights {' '.join(args)}: {type(error).__name__}: {error})"


def main() -> int:
    checked_at = datetime.now(timezone.utc)
    root = profile_root()
    knowledge = root / "knowledge"
    reports = knowledge / "cost-reports"
    reports.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Audit de cout modeles — {DAYS} jours",
        "",
        f"- Collecte UTC: {checked_at.isoformat()}",
        "",
        "## Insights globaux",
        "```",
        insights(),
        "```",
    ]
    for profile in KEY_PROFILES:
        lines += [
            f"## Profil {profile}",
            "```",
            insights("-p", profile),
            "```",
        ]

    stamp = checked_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = reports / f"{stamp}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = [
        "# État audit de cout",
        "",
        f"Dernière collecte: {checked_at.isoformat()}",
        f"Rapport: `{report_path}`",
        f"Profils analyses: {len(KEY_PROFILES)} + global",
        "",
    ]
    (knowledge / "COST_STATUS.md").write_text("\n".join(status), encoding="utf-8")

    print(f"MODEL_COST_AUDIT days={DAYS} profiles={len(KEY_PROFILES)}")
    print(f"report={report_path}")
    print("VERDICT=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - cron ne doit jamais casser
        print(f"MODEL_COST_AUDIT_ERROR={type(error).__name__}: {error}")
        print("VERDICT=SUPERVISION_REQUISE")
        raise SystemExit(0)
