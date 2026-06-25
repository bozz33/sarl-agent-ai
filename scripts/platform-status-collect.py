#!/usr/bin/env python3
"""Collecteur read-only de l'état plateforme SARL-Agent-AI.

Agrège, depuis tous les profils Hermes, les jobs cron (isolés par profil) et le
Kanban partagé, puis produit un snapshot fichier et un digest Telegram.

STRICTEMENT LECTURE SEULE : n'appelle que `hermes ... cron list` et
`hermes kanban list`. Aucune mutation (pas de create/remove/move/update).
Aucun CLI exposé au bot Telegram : ce script tourne côté hôte.

Usage :
    python3 scripts/platform-status-collect.py            # snapshot + print (pas d'envoi)
    python3 scripts/platform-status-collect.py --send     # + digest Telegram
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTAINER = "sarl-hermes-agent"
HERMES = "/opt/hermes/.venv/bin/hermes"
OUT_DIR = ROOT / "reports" / "platform-status"
SECRETS = ROOT / ".secrets" / "telegram.env"

PROFILES = (
    "sarl-router", "sarl-orchestrator", "sarl-orchestrator-critical",
    "sarl-governor", "sarl-stack-steward", "research-sage", "docs-scribe",
    "code-builder", "codex-builder", "code-reviewer", "code-reviewer-critical",
    "qa-agent", "ops-foundation", "cpanel-watch-agent", "security-audit-agent",
    "community-manager", "support-agent", "bureau-etudes-agent",
    "designer-3d-agent",
)
KANBAN_STATUSES = (
    "triage", "todo", "ready", "running", "review", "blocked", "done",
    "scheduled", "archived",
)


def _hermes(args: list[str]) -> str:
    """Exécute une commande hermes LECTURE SEULE dans le conteneur."""
    try:
        r = subprocess.run(
            ["docker", "exec", CONTAINER, HERMES, *args],
            capture_output=True, text=True, timeout=90,
        )
        return r.stdout
    except subprocess.TimeoutExpired:
        return ""


def collect_crons() -> dict[str, list[dict]]:
    """Liste les jobs cron par profil (cron list est isolé par profil)."""
    result: dict[str, list[dict]] = {}
    for profile in PROFILES:
        out = _hermes(["-p", profile, "cron", "list"])
        jobs = []
        name = sched = state = None
        for line in out.splitlines():
            m = re.search(r"\[(active|disabled|paused)\]", line)
            if m:
                state = m.group(1)
            m = re.search(r"Name:\s+(.*)", line)
            if m:
                name = m.group(1).strip()
            m = re.search(r"Schedule:\s+(.*)", line)
            if m:
                sched = m.group(1).strip()
                if name:
                    jobs.append({"name": name, "schedule": sched, "state": state})
                    name = sched = state = None
        if jobs:
            result[profile] = jobs
    return result


def collect_kanban() -> dict:
    """Lit le board Kanban partagé (JSON) et agrège par statut."""
    raw = _hermes(["kanban", "list", "--json"])
    try:
        tasks = json.loads(raw) if raw.strip() else []
    except json.JSONDecodeError:
        tasks = []
    by_status: dict[str, int] = {s: 0 for s in KANBAN_STATUSES}
    open_tasks = []
    for t in tasks:
        st = t.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        if st in {"ready", "running", "review", "blocked"}:
            open_tasks.append({
                "id": t.get("id"), "status": st,
                "assignee": t.get("assignee") or "unassigned",
                "title": (t.get("title") or "")[:80],
            })
    return {"total": len(tasks), "by_status": by_status, "open": open_tasks}


def build_digest(crons: dict, kanban: dict, ts: str) -> str:
    total_jobs = sum(len(v) for v in crons.values())
    lines = [
        "RAPPORT_PLATFORM_STATUS",
        f"DATE: {ts}",
        "SOURCE: platform-status-collect.py (lecture seule)",
        "",
        "RÉSUMÉ:",
        f"- Profils avec cron actif: {len(crons)}",
        f"- Jobs cron au total: {total_jobs}",
        f"- Tâches Kanban: {kanban['total']}",
        f"- Ouvertes (ready/running/review): "
        f"{kanban['by_status'].get('ready',0)+kanban['by_status'].get('running',0)+kanban['by_status'].get('review',0)}",
        f"- Bloquées: {kanban['by_status'].get('blocked',0)}",
        f"- Terminées: {kanban['by_status'].get('done',0)}",
        "",
        "CRONS_PAR_PROFIL:",
    ]
    for profile, jobs in crons.items():
        lines.append(f"- {profile}:")
        for j in jobs:
            lines.append(f"    - {j['name']} ({j['schedule']}) [{j['state']}]")
    lines += ["", "KANBAN:"]
    for st in KANBAN_STATUSES:
        n = kanban["by_status"].get(st, 0)
        if n:
            lines.append(f"- {st}: {n}")
    if kanban["open"]:
        lines += ["", "TÂCHES_OUVERTES:"]
        for t in kanban["open"]:
            lines.append(f"- [{t['status']}] {t['id']} {t['assignee']}: {t['title']}")
    return "\n".join(lines)


def send_telegram(text: str) -> None:
    env = {}
    for line in SECRETS.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat = env.get("TELEGRAM_HOME_CHANNEL")
    if not token or not chat:
        print("Telegram: token/chat absent, envoi ignoré")
        return
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:4000]}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as r:
        print("Telegram:", r.status)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="envoyer le digest Telegram")
    args = parser.parse_args()

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    crons = collect_crons()
    kanban = collect_kanban()
    digest = build_digest(crons, kanban, ts)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "latest.md").write_text(digest + "\n", encoding="utf-8")
    (OUT_DIR / f"{ts}.md").write_text(digest + "\n", encoding="utf-8")
    (OUT_DIR / "latest.json").write_text(
        json.dumps({"ts": ts, "crons": crons, "kanban": kanban}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(digest)
    if args.send:
        send_telegram(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
