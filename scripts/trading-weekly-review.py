#!/usr/bin/env python3
"""Weekly trading review — Option C.

A --no-agent cron on the DEFAULT profile (whose gateway runs, so it fires
reliably) invokes the trading-research-agent ONE-SHOT for the intelligent work:
analyse the week's backtests, write one validated lesson to project memory, and
open a Kanban review task. The agent's report is printed and the cron delivers
it to Telegram. DeepSeek (gemini-free), on-demand — no persistent gateway, no
orchestrator routing. Backtest/simulation only.
"""

from __future__ import annotations

import subprocess

HERMES = "/opt/hermes/bin/hermes"
PROFILE = "trading-research-agent"
PROMPT = (
    "Revue hebdomadaire du module trading (BACKTEST ONLY). "
    "1) Appelle nautilus_run_mission name=weekly_trading_review via le MCP sarl_nautilus_runner. "
    "2) Analyse les backtests de la semaine: performance, win rate, erreurs recurrentes. "
    "3) Ecris UNE lecon validee et concise via l'outil d'ecriture du MCP sarl_project_memory "
    "(store/save). Si le MCP est indisponible, ecris la lecon dans un fichier data/trading/lessons/. "
    "4) Cree une tache Kanban de revue trading (titre clair, a valider par un humain). "
    "Produis un rapport court de 5 a 8 lignes. "
    "Aucun live, aucun broker, aucune modification de regle sans validation humaine."
)


def main() -> int:
    try:
        r = subprocess.run(
            [HERMES, "-p", PROFILE, "-z", PROMPT, "--yolo"],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("[trading-weekly-review] agent timed out")
        return 1
    out = (r.stdout or "").strip()
    if not out:
        print("[trading-weekly-review] empty agent output", r.stderr[-300:] if r.stderr else "")
        return 1
    print("📈 TRADING DEMO — WEEKLY REVIEW (backtest only, no live)")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
