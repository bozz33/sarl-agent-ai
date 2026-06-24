#!/usr/bin/env python3
"""Collecte deterministe de l'etat du Kanban pour les syntheses recurrentes.

Porte par des crons du profil sarl-orchestrator (toute mission entre par
l'orchestrateur central). Le script appelle `hermes kanban` en lecture seule
(stats + liste JSON) et ecrit un rapport date que l'orchestrateur analyse ensuite
selon l'angle voulu (support, operations, hebdomadaire...).

Robuste: toute exception est capturee, verdict SUPERVISION_REQUISE imprime, code
de sortie 0 pour ne pas casser le tick cron.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


HERMES = "/opt/hermes/.venv/bin/hermes"


def profile_root() -> Path:
    # /opt/data/profiles/<profile>/scripts/kanban-summary-collect.py
    return Path(__file__).resolve().parent.parent


def kanban(*args: str) -> str:
    try:
        result = subprocess.run(
            [HERMES, "kanban", *args],
            text=True,
            capture_output=True,
            timeout=90,
        )
        out = (result.stdout or "").strip()
        return out or (result.stderr or "").strip() or "(aucune donnee)"
    except Exception as error:  # noqa: BLE001
        return f"(echec kanban {' '.join(args)}: {type(error).__name__}: {error})"


def main() -> int:
    checked_at = datetime.now(timezone.utc)
    root = profile_root()
    knowledge = root / "knowledge"
    reports = knowledge / "kanban-reports"
    reports.mkdir(parents=True, exist_ok=True)

    lines = [
        "# État Kanban",
        "",
        f"- Collecte UTC: {checked_at.isoformat()}",
        "",
        "## Boards",
        "```",
        kanban("boards"),
        "```",
        "## Statistiques",
        "```",
        kanban("stats"),
        "```",
        "## Taches ouvertes (ready)",
        "```",
        kanban("list", "--status", "ready", "--json"),
        "```",
        "## Taches bloquees (blocked)",
        "```",
        kanban("list", "--status", "blocked", "--json"),
        "```",
        "## Taches en revue (review)",
        "```",
        kanban("list", "--status", "review", "--json"),
        "```",
    ]

    stamp = checked_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = reports / f"{stamp}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = [
        "# État synthèse Kanban",
        "",
        f"Dernière collecte: {checked_at.isoformat()}",
        f"Rapport: `{report_path}`",
        "",
    ]
    (knowledge / "KANBAN_STATUS.md").write_text("\n".join(status), encoding="utf-8")

    print("KANBAN_SUMMARY")
    print(f"report={report_path}")
    print("VERDICT=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - cron ne doit jamais casser
        print(f"KANBAN_SUMMARY_ERROR={type(error).__name__}: {error}")
        print("VERDICT=SUPERVISION_REQUISE")
        raise SystemExit(0)
