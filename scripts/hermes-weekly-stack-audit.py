#!/usr/bin/env python3
"""Deterministic weekly SARL stack audit for Hermes no-agent cron."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPORT = Path("/opt/sarl-observability/latest.txt")
MAX_REPORT_AGE_SECONDS = 20 * 60
RELEASES = {
    "Hermes Agent": "https://api.github.com/repos/NousResearch/hermes-agent/releases/latest",
    "Hermes Workspace": "https://api.github.com/repos/outsourc-e/hermes-workspace/releases/latest",
}


def fetch_release(url: str) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "sarl-agent-ai-weekly-audit",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.load(response)
        return str(payload.get("tag_name") or "unknown"), str(
            payload.get("html_url") or url
        )
    except (OSError, ValueError, urllib.error.URLError):
        return "unknown", url


def section(text: str, name: str) -> list[str]:
    marker = f"[{name}]"
    if marker not in text:
        return []
    tail = text.split(marker, 1)[1]
    body = tail.split("\n[", 1)[0]
    return [line.strip() for line in body.splitlines() if line.strip()]


def main() -> int:
    now = datetime.now(timezone.utc)
    problems: list[str] = []
    unknowns: list[str] = []

    if not REPORT.is_file():
        print("ETAT_GLOBAL=INCONNU")
        print(f"INCIDENT=Rapport hôte absent: {REPORT}")
        print("VERDICT=SUPERVISION_REQUISE")
        return 0

    text = REPORT.read_text(encoding="utf-8", errors="replace")
    collected_match = re.search(r"^COLLECTED_AT_UTC=(.+)$", text, re.MULTILINE)
    collected = collected_match.group(1) if collected_match else "unknown"
    if collected_match:
        try:
            collected_at = datetime.fromisoformat(collected.replace("Z", "+00:00"))
            age = (now - collected_at).total_seconds()
            if age > MAX_REPORT_AGE_SECONDS:
                problems.append(f"rapport hôte périmé ({int(age)}s)")
        except ValueError:
            unknowns.append("date du rapport hôte illisible")
    else:
        unknowns.append("date du rapport hôte absente")

    compose = section(text, "COMPOSE")
    endpoints = section(text, "ENDPOINTS")
    timers = section(text, "TIMERS")
    logs = section(text, "RECENT_LOG_COUNTS_30M")

    for line in compose:
        if "healthy" not in line and "sandbox-docker" not in line:
            problems.append(f"service non healthy: {line}")
    if len(compose) < 4:
        problems.append(f"services Compose incomplets: {len(compose)}/4")

    for line in endpoints:
        if line.startswith("hermes_health=") and '"status": "ok"' not in line:
            problems.append("Hermes health non OK")
        if line.startswith("workspace_http=") and not line.endswith("200"):
            problems.append(f"Workspace HTTP non OK: {line}")

    for line in timers:
        if "active=active" not in line or "enabled=enabled" not in line:
            problems.append(f"timer non opérationnel: {line}")

    for line in logs:
        match = re.search(r"errors=(\d+)", line)
        if match and int(match.group(1)) > 0:
            problems.append(f"erreurs récentes: {line}")

    releases = {name: fetch_release(url) for name, url in RELEASES.items()}
    if any(tag == "unknown" for tag, _ in releases.values()):
        unknowns.append("une ou plusieurs releases officielles injoignables")

    print("AUDIT_HEBDOMADAIRE_SARL")
    print(f"COLLECTED_AT_UTC={collected}")
    print("FAITS_SERVICES:")
    for line in compose:
        print(f"- {line}")
    print("FAITS_ENDPOINTS:")
    for line in endpoints:
        print(f"- {line}")
    print("FAITS_TIMERS:")
    for line in timers:
        print(f"- {line}")
    print("VERSIONS_OFFICIELLES:")
    for name, (tag, url) in releases.items():
        print(f"- {name}: {tag} source={url}")
    print("LIMITES:")
    print("- Images SARL personnalisées: comparer commits/digests avant toute mise à jour.")
    print("- Aucun avis CVE n'est affirmé sans source de vulnérabilité dédiée et vérification locale.")
    print("INCIDENTS:")
    if problems:
        for problem in problems:
            print(f"- {problem}")
    else:
        print("- aucun incident prouvé")
    print("INCONNUS:")
    if unknowns:
        for unknown in unknowns:
            print(f"- {unknown}")
    else:
        print("- aucun")
    print("ACTIONS:")
    if problems or unknowns:
        print("- Investigation humaine requise; aucune modification automatique.")
        print("APPROBATION_REQUISE=OUI avant correctif")
        print("VERDICT=SUPERVISION_REQUISE")
    else:
        print("- aucune modification requise")
        print("VERDICT=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
