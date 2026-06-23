#!/usr/bin/env python3
"""Install expert profile files and idempotent official-learning cron jobs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTAINER = "sarl-hermes-agent"
HERMES = "/opt/hermes/.venv/bin/hermes"

PROFILES = {
    "designer-3d-agent": {
        "skill": "design-3d-production",
        "schedule": "10 4 * * 2",
        "job": "learn:designer-3d-agent:official",
        "domain": "Blender, FreeCAD, glTF, USD, MaterialX et OpenColorIO",
    },
    "bureau-etudes-agent": {
        "skill": "engineering-design-office",
        "schedule": "20 4 * * 3",
        "job": "learn:bureau-etudes-agent:official",
        "domain": "Eurocodes, annexes nationales, IFC, IDS, bSDD et FreeCAD",
    },
    "community-manager": {
        "skill": "community-content-operations",
        "schedule": "30 4 * * 4",
        "job": "learn:community-manager:official",
        "domain": "Meta, LinkedIn, YouTube, TikTok, X et protection des données",
    },
}


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def docker_exec(*args: str, capture: bool = False) -> str:
    return run("docker", "exec", CONTAINER, *args, capture=capture)


def hermes_exec(profile: str, *args: str) -> None:
    run(
        "docker",
        "exec",
        "-u",
        "hermes",
        CONTAINER,
        HERMES,
        "-p",
        profile,
        *args,
    )


def copy_profile_files(profile: str, skill: str) -> None:
    source = ROOT / "profiles" / profile
    destination = f"/opt/data/profiles/{profile}"
    docker_exec(
        "mkdir",
        "-p",
        f"{destination}/knowledge/official-research",
        f"{destination}/skills/custom",
        f"{destination}/cron",
        f"{destination}/scripts",
    )
    for relative in ("SOUL.md", "KNOWLEDGE_POLICY.md", "knowledge/CURRENT.md"):
        run(
            "docker",
            "cp",
            str(source / relative),
            f"{CONTAINER}:{destination}/{relative}",
        )
    docker_exec("rm", "-rf", f"{destination}/skills/custom/{skill}")
    run(
        "docker",
        "cp",
        str(ROOT / "skills" / "custom" / skill),
        f"{CONTAINER}:{destination}/skills/custom/{skill}",
    )
    run(
        "docker",
        "cp",
        str(ROOT / "scripts" / "hermes-official-source-watch.py"),
        f"{CONTAINER}:{destination}/scripts/official-source-watch.py",
    )
    docker_exec(
        "chown",
        "-R",
        "hermes:hermes",
        f"{destination}/SOUL.md",
        f"{destination}/KNOWLEDGE_POLICY.md",
        f"{destination}/knowledge",
        f"{destination}/skills/custom/{skill}",
        f"{destination}/cron",
        f"{destination}/scripts/official-source-watch.py",
    )
    docker_exec("chmod", "750", f"{destination}/scripts/official-source-watch.py")


def jobs_for(profile: str) -> list[dict]:
    try:
        raw = docker_exec(
            "cat",
            f"/opt/data/profiles/{profile}/cron/jobs.json",
            capture=True,
        )
    except subprocess.CalledProcessError:
        return []
    if not raw.strip():
        return []
    return json.loads(raw).get("jobs", [])


def learning_prompt(profile: str, skill: str, domain: str) -> str:
    destination = f"/opt/data/profiles/{profile}/knowledge"
    return (
        f"Veille autonome officielle pour {domain}. "
        f"Charge skill {skill}, SOUL.md, KNOWLEDGE_POLICY.md, {destination}/CURRENT.md, "
        f"{destination}/SOURCE_STATUS.md et le dernier rapport de "
        f"{destination}/official-research/ (déjà produit de façon déterministe par le "
        "script de veille; son résumé t'est injecté). Lis les références officielles du skill. "
        "Analyse seulement les changements publiés depuis la dernière synthèse. "
        "Distingue FAIT, INFERENCE, INCONNU. Vérifie URL, date, version et portée. "
        "N'APPLIQUE RIEN automatiquement. N'altère ni CURRENT.md, ni SOUL.md, ni le skill. "
        f"Écris ta proposition de connaissances consolidées dans {destination}/CURRENT.proposed.md "
        "(remplace ce fichier s'il existe), en conservant contradictions et limites, et en "
        "incluant les changements proposés de SOUL/skill comme propositions étiquetées pour revue humaine. "
        "Aucune publication, achat, signature ou action externe. "
        "Le détail complet va dans CURRENT.proposed.md; le rapport Telegram doit être CONCIS "
        "(≈25 lignes max, pas de longues citations). "
        "Termine OBLIGATOIREMENT avec un final_response = RAPPORT Telegram structuré et bref: "
        "1) Module et date; 2) Sources consultées (compte + URLs clés); 3) Changements détectés "
        "(FAIT/INFERENCE/INCONNU, 1 ligne chacun); 4) Résumé proposition CURRENT.md (3-5 puces); "
        "5) Propositions SOUL/skill éventuelles (sinon « aucune »); 6) Risques/inconnues (bref); "
        "7) DEMANDE DE VALIDATION explicite en dernière ligne — "
        f"« Valider: réponds valide:{profile} — Annuler: rejette:{profile} ». "
        "Si aucun changement officiel: dis-le clairement et n'écris pas de proposition."
    )


def install_job(profile: str, spec: dict) -> None:
    jobs = jobs_for(profile)
    existing = next((job for job in jobs if job.get("name") == spec["job"]), None)
    prompt = learning_prompt(profile, spec["skill"], spec["domain"])
    if existing:
        hermes_exec(
            profile,
            "cron",
            "edit",
            str(existing["id"]),
            "--schedule",
            spec["schedule"],
            "--prompt",
            prompt,
            "--name",
            spec["job"],
            "--deliver",
            "telegram",
            "--script",
            "official-source-watch.py",
            "--agent",
            "--skill",
            spec["skill"],
            "--workdir",
            "/workspace",
        )
    else:
        hermes_exec(
            profile,
            "cron",
            "create",
            spec["schedule"],
            prompt,
            "--name",
            spec["job"],
            "--deliver",
            "telegram",
            "--script",
            "official-source-watch.py",
            "--skill",
            spec["skill"],
            "--workdir",
            "/workspace",
        )


def main() -> int:
    for profile, spec in PROFILES.items():
        copy_profile_files(profile, spec["skill"])
        install_job(profile, spec)
        print(f"{profile}: expert files and learning job installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
