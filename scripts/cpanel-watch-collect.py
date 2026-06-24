#!/usr/bin/env python3
"""Collecte deterministe lecture seule de l'etat cPanel LWS via SSH.

Concu pour le cron `daily-ops-cpanel-watch` du profil cpanel-watch-agent.
Le script SSH n'execute que des commandes en lecture; il n'ecrit jamais sur le
serveur distant. Il produit un rapport date dans
`<profil>/knowledge/cpanel-reports/<stamp>.md` que l'agent resume ensuite.

Robuste par conception: toute exception est capturee, un verdict
SUPERVISION_REQUISE est imprime et le code de sortie reste 0 pour ne pas casser
le tick cron.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


SSH_CONFIG = "/opt/hermes-ssh/config"
SSH_HOST = "blocksdevs"
SSH_TIMEOUT = 45

# Bundle de commandes STRICTEMENT en lecture seule, une seule connexion SSH.
REMOTE_SCRIPT = r"""
set -o pipefail 2>/dev/null
echo '###UPTIME'; uptime 2>/dev/null
echo '###DISK'; df -h "$HOME" / 2>/dev/null
echo '###HOMEUSE'; du -sh "$HOME/public_html" 2>/dev/null
echo '###DOMAINS'; ls -1d "$HOME"/public_html "$HOME"/*/public_html 2>/dev/null
echo '###MODIFIED24H'; find "$HOME/public_html" -type f -mtime -1 2>/dev/null | head -50
echo '###SUSPECT'; find "$HOME/public_html" -type f -name '*.php' -mtime -7 2>/dev/null \
  | head -2000 | xargs -r grep -lsE 'base64_decode|eval\(|gzinflate|str_rot13|shell_exec|passthru' 2>/dev/null \
  | head -20
echo '###MAILDOMAINS'; ls -1 "$HOME/etc" 2>/dev/null
echo '###MAILACCOUNTS'; for d in "$HOME"/etc/*/; do dom=$(basename "$d"); n=$(wc -l < "$d/passwd" 2>/dev/null); echo "$dom: ${n:-0} comptes"; done
echo '###END'
""".strip()


def profile_root() -> Path:
    # /opt/data/profiles/<profile>/scripts/cpanel-watch-collect.py
    return Path(__file__).resolve().parent.parent


def run_ssh() -> str:
    result = subprocess.run(
        [
            "ssh",
            "-F",
            SSH_CONFIG,
            "-o",
            f"ConnectTimeout={SSH_TIMEOUT}",
            "-o",
            "BatchMode=yes",
            SSH_HOST,
            "bash -s",
        ],
        input=REMOTE_SCRIPT,
        text=True,
        capture_output=True,
        timeout=SSH_TIMEOUT + 60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ssh rc={result.returncode}: {result.stderr.strip()[:400]}"
        )
    return result.stdout


def parse_sections(raw: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in raw.splitlines():
        if line.startswith("###"):
            current = line[3:].strip()
            if current != "END":
                sections[current] = []
            continue
        if current and current != "END":
            stripped = line.rstrip()
            if stripped:
                sections[current].append(stripped)
    return sections


def main() -> int:
    checked_at = datetime.now(timezone.utc)
    root = profile_root()
    knowledge = root / "knowledge"
    reports = knowledge / "cpanel-reports"
    reports.mkdir(parents=True, exist_ok=True)

    raw = run_ssh()
    sec = parse_sections(raw)

    modified = sec.get("MODIFIED24H", [])
    suspect = sec.get("SUSPECT", [])
    verdict = "SUPERVISION_REQUISE" if suspect else "OK"

    lines = [
        f"# Collecte cPanel LWS — {SSH_HOST}",
        "",
        f"- Collecte UTC: {checked_at.isoformat()}",
        f"- Hote: {SSH_HOST}",
        f"- Fichiers modifies 24h: {len(modified)}",
        f"- Fichiers PHP suspects (7j): {len(suspect)}",
        "",
        "## Uptime / charge",
        "```",
        *sec.get("UPTIME", ["(indisponible)"]),
        "```",
        "## Disque",
        "```",
        *sec.get("DISK", ["(indisponible)"]),
        "```",
        "## Usage public_html",
        "```",
        *sec.get("HOMEUSE", ["(indisponible)"]),
        "```",
        "## Domaines / public_html",
        "```",
        *sec.get("DOMAINS", ["(aucun)"]),
        "```",
        "## Comptes email par domaine (noms de domaines uniquement, sans secret)",
        "```",
        *sec.get("MAILACCOUNTS", ["(aucun)"]),
        "```",
        "## Fichiers modifies dernieres 24h (max 50)",
        "```",
        *(modified or ["(aucun)"]),
        "```",
        "## Fichiers PHP a motifs suspects (max 20)",
        "```",
        *(suspect or ["(aucun)"]),
        "```",
    ]

    stamp = checked_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = reports / f"{stamp}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = [
        f"# État cPanel — {SSH_HOST}",
        "",
        f"Dernière collecte: {checked_at.isoformat()}",
        f"Rapport: `{report_path}`",
        f"Fichiers modifiés 24h: {len(modified)}",
        f"Fichiers suspects: {len(suspect)}",
        f"Verdict: {verdict}",
        "",
    ]
    (knowledge / "CPANEL_STATUS.md").write_text("\n".join(status), encoding="utf-8")

    print(f"CPANEL_WATCH host={SSH_HOST}")
    print(f"modified_24h={len(modified)} suspect={len(suspect)}")
    print(f"report={report_path}")
    print(f"VERDICT={verdict}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - cron ne doit jamais casser
        print(f"CPANEL_WATCH_ERROR={type(error).__name__}: {error}")
        print("VERDICT=SUPERVISION_REQUISE")
        raise SystemExit(0)
