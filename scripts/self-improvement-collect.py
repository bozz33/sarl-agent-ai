#!/usr/bin/env python3
"""Collecte deterministe du contexte pour la revue d'auto-amelioration supervisee.

Porte par le cron `weekly-self-improvement-review` du profil sarl-orchestrator.
Agrege en lecture seule les rapports recents produits par les missions (cpanel,
cout, kanban, gouvernance) et les propositions de connaissance des jobs
d'apprentissage (CURRENT.proposed.md), pour que l'orchestrateur PROPOSE des
ameliorations de skills/SOUL/procedures — jamais ne les applique.

Robuste: toute exception capturee, verdict SUPERVISION_REQUISE, sortie 0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


PROFILES_ROOT = Path("/opt/data/profiles")
REPORT_DIRS = ("cpanel-reports", "cost-reports", "kanban-reports", "official-research")
MAX_CHARS_PER_FILE = 4000


def latest_file(directory: Path) -> Path | None:
    if not directory.is_dir():
        return None
    files = sorted(
        (p for p in directory.glob("*.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def excerpt(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as error:  # noqa: BLE001
        return f"(lecture impossible: {error})"
    if len(text) > MAX_CHARS_PER_FILE:
        text = text[:MAX_CHARS_PER_FILE] + "\n... [tronque]"
    return text


def profile_root() -> Path:
    # /opt/data/profiles/<profile>/scripts/self-improvement-collect.py
    return Path(__file__).resolve().parent.parent


def main() -> int:
    checked_at = datetime.now(timezone.utc)
    root = profile_root()
    knowledge = root / "knowledge"
    out_dir = knowledge / "improvement-context"
    out_dir.mkdir(parents=True, exist_ok=True)
    # S'assurer que le dossier des propositions existe pour l'agent.
    (knowledge / "improvement-proposals").mkdir(parents=True, exist_ok=True)

    lines = [
        "# Contexte d'auto-amelioration",
        "",
        f"- Collecte UTC: {checked_at.isoformat()}",
        "",
        "## Rapports recents par profil",
    ]

    if PROFILES_ROOT.is_dir():
        for profile_dir in sorted(PROFILES_ROOT.iterdir()):
            if not profile_dir.is_dir():
                continue
            kn = profile_dir / "knowledge"
            found: list[tuple[str, Path]] = []
            for rd in REPORT_DIRS:
                f = latest_file(kn / rd)
                if f:
                    found.append((rd, f))
            proposed = kn / "CURRENT.proposed.md"
            if proposed.is_file():
                found.append(("knowledge-proposal", proposed))
            if not found:
                continue
            lines.append(f"### {profile_dir.name}")
            for label, f in found:
                lines += [
                    f"#### {label} — {f.name}",
                    "```",
                    excerpt(f),
                    "```",
                ]

    # Propositions d'amelioration deja en attente de revue humaine.
    pending = sorted((knowledge / "improvement-proposals").glob("*.md"))
    lines += ["", "## Propositions deja en attente de revue"]
    if pending:
        for p in pending:
            lines.append(f"- {p.name}")
    else:
        lines.append("- (aucune)")

    stamp = checked_at.strftime("%Y-%m-%dT%H%M%SZ")
    report_path = out_dir / f"{stamp}.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("SELF_IMPROVEMENT_CONTEXT")
    print(f"report={report_path}")
    print(f"pending_proposals={len(pending)}")
    print("VERDICT=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - cron ne doit jamais casser
        print(f"SELF_IMPROVEMENT_ERROR={type(error).__name__}: {error}")
        print("VERDICT=SUPERVISION_REQUISE")
        raise SystemExit(0)
