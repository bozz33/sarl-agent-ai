#!/usr/bin/env python3
"""Persist substantial Telegram missions into the shared Hermes Kanban board."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/opt/data"))
STATE_DB = HERMES_HOME / "state.db"
INDEX_FILE = HERMES_HOME / "telegram-work-tracking.json"
HERMES_BIN = os.environ.get("HERMES_BIN", "/opt/hermes/.venv/bin/hermes")
BOARD = os.environ.get("HERMES_KANBAN_BOARD", "sarl-agent-ai")
DEFAULT_READY_LOW_RISK = os.environ.get("TELEGRAM_READY_LOW_RISK", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}
TELEGRAM_SYNC_NOTIFY = os.environ.get("TELEGRAM_SYNC_NOTIFY", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}

ACTION_VERBS = re.compile(
    r"\b(cr[eé]e(?:r|z)?|fais|faire|effectue(?:r|z)?|r[eé]alise(?:r|z)?|"
    r"d[eé]veloppe(?:r|z)?|corrige(?:r|z)?|analyse(?:r|z)?|audite(?:r|z)?|"
    r"pr[eé]pare(?:r|z)?|r[eé]dige(?:r|z)?|impl[eé]mente(?:r|z)?|"
    r"mets?\s+en\s+place|d[eé]ploie(?:r|z)?|modifie(?:r|z)?|construis|"
    r"construire|lance(?:r|z)?|g[eé]n[eè]re(?:r|z)?|teste(?:r|z)?|"
    r"v[eé]rifie(?:r|z)?|installe(?:r|z)?|configure(?:r|z)?|"
    r"recherche(?:r|z)?|organise(?:r|z)?|supervise(?:r|z)?|"
    r"create|build|implement|fix|analy[sz]e|audit|prepare|write|deploy|"
    r"modify|launch|generate|test|verify|install|configure|research|"
    r"organize|monitor|set\s+up)\b",
    re.I,
)
WORK_NOUNS = re.compile(
    r"\b(mission|projet|project|t[aâ]che|task|rapport|report|livrable|"
    r"deliverable|fonctionnalit[eé]|feature|application|site|serveur|server|"
    r"audit|analyse|migration|d[eé]ploiement|deployment|supervision)\b",
    re.I,
)
PURE_QUESTION = re.compile(
    r"^(est[- ]ce que|pourquoi|comment|qu(?:'|’)est[- ]ce que|quelle?s?\b|"
    r"quel?s?\b|o[uù]\b|when\b|why\b|how\b|what\b|where\b|is\b|are\b|"
    r"do\b|does\b|can you tell me\b)",
    re.I,
)
IMPORTANT_SCOPE = re.compile(
    r"\b(projet|project|plateforme|platform|production|prod|syst[eè]me|system|"
    r"infrastructure|stack|s[eé]curit[eé]|security|d[eé]ploiement|deployment|"
    r"migration|base de donn[eé]es|database|architecture|int[eé]gration|"
    r"integration|automatisation|automation|automatique|automatic|"
    r"orchestrat(?:eur|ion)|workflow|telegram|api|workspace|hermes|incident|"
    r"audit|serveur|server|cpanel|vps|site|email)\b",
    re.I,
)
DURABLE_OUTPUT = re.compile(
    r"\b(patch|code|configuration|config|rapport complet|full report|"
    r"plan d['’]ex[eé]cution|implementation plan|livrable|deliverable|"
    r"documentation|runbook|tests?|backup|rollback|monitoring|surveillance|"
    r"suivi|tracking|baseline|script)\b",
    re.I,
)
HIGH_RISK_ACTION = re.compile(
    r"\b(d[eé]ploie|deploy|installe|install|migre|migrate|red[eé]marre|"
    r"restart|supprime|delete|configure|s[eé]curise|secure|corrige|fix|"
    r"impl[eé]mente|implement|modifie|modify|publie|publish|connecte|"
    r"connexion|ssh)\b",
    re.I,
)
EXPLICIT_TRACKING = re.compile(
    r"\b(cr[eé]e|ouvre|ajoute|enregistre|suis|track|affecte)\b.{0,60}"
    r"\b(t[aâ]che|task|kanban|mission|projet|project|job)\b",
    re.I,
)
DEPLOY_INTENT = re.compile(
    r"\b(d[eé]ploie(?:r|z)?|deploy(?:ment)?|mise en prod|production|prod\b|"
    r"release|publie(?:r|z)?|publish)\b",
    re.I,
)
INCIDENT_INTENT = re.compile(
    r"\b(incident|panne|down|hors ligne|offline|urgence|urgent|alerte|"
    r"bloqu[eé]|crash|erreur 5\d\d|outage)\b",
    re.I,
)
RESEARCH_INTENT = re.compile(
    r"\b(recherche(?:r|z)?|veille|benchmark|compare|comparatif|analyse(?:r|z)?|"
    r"audit(?:e|er|ez)?|r[eé]sum[eé]|synth[eè]se|rapport)\b",
    re.I,
)
REMINDER_INTENT = re.compile(
    r"\b(rappel|remind(?:er)?|pense[- ]?b[eê]te|relance(?:r|z)?|follow[- ]?up)\b",
    re.I,
)
TASK_INTENT = re.compile(
    r"\b(t[aâ]che|mission|job|kanban|impl[eé]mente(?:r|z)?|corrige(?:r|z)?|"
    r"pr[eé]pare(?:r|z)?|r[eé]dige(?:r|z)?|cr[eé]e(?:r|z)?|fais|faire|"
    r"effectue(?:r|z)?|build|implement|fix|prepare|write|create)\b",
    re.I,
)
HIGH_RISK_SCOPE = re.compile(
    r"\b(production|prod\b|d[eé]ploiement|deployment|migration|base de donn[eé]es|"
    r"database|db\b|suppression|delete|secrets?|tokens?|cl[eé]s? api|api keys?|"
    r"s[eé]curit[eé]|security|paiement|payment|contrat|juridique|legal|rgpd|"
    r"donn[eé]es personnelles|vps|dns|reverse proxy|ssh|root|rollback|backup|"
    r"irr[eé]versible|client important)\b",
    re.I,
)
MEDIUM_RISK_SCOPE = re.compile(
    r"\b(code|patch|configuration|config|api|workspace|hermes|stack|serveur|"
    r"server|automatisation|automation|int[eé]gration|integration|cpanel|site|email)\b",
    re.I,
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def base_trackable_score(message: str) -> tuple[bool, int, int]:
    text = normalize(message)
    lowered = text.lower()
    if (
        len(text) < 20
        or text.startswith("[The user sent")
        or re.match(r"^(ok\s+|oui\s+|non\s+)?(?:moi\s+)?je suis\b", lowered)
        or re.search(r"\best[- ]ce qu", lowered)
        or re.match(r"^la recr[eé]ation .+ est lanc[eé]e\b", lowered)
        or (
            re.search(r"\bplusieurs t[aâ]ches?\b", lowered)
            and not EXPLICIT_TRACKING.search(text)
        )
    ):
        return False, 0, 0
    question_candidate = re.sub(
        r"^(ok|oui|non|regarde|aussi|alors|stp|s'il te pla[iî]t)[, :;-]*",
        "",
        text,
        flags=re.I,
    )
    if PURE_QUESTION.search(question_candidate):
        return False, 0, 0
    if EXPLICIT_TRACKING.search(text):
        return True, 99, 1
    if re.search(r"\b\d+\s+sites?\s+[àa]\s+analyser\b", text, re.I):
        return True, 99, 1
    action_count = len(ACTION_VERBS.findall(text))
    if action_count == 0:
        return False, 0, 0
    score = 0
    score += 1 if ACTION_VERBS.search(text) else 0
    score += 2 if IMPORTANT_SCOPE.search(text) else 0
    score += 1 if DURABLE_OUTPUT.search(text) else 0
    score += 2 if HIGH_RISK_ACTION.search(text) else 0
    score += 1 if WORK_NOUNS.search(text) else 0
    score += 1 if action_count >= 2 else 0
    score += 1 if len(text) >= 220 else 0
    return score >= 5, score, action_count


def classify_message(message: str) -> dict[str, str | int | bool]:
    text = normalize(message)
    trackable, score, action_count = base_trackable_score(text)
    question_candidate = re.sub(
        r"^(ok|oui|non|regarde|aussi|alors|stp|s'il te pla[iî]t)[, :;-]*",
        "",
        text,
        flags=re.I,
    )

    if PURE_QUESTION.search(question_candidate):
        intent = "question"
    elif INCIDENT_INTENT.search(text):
        intent = "incident"
    elif DEPLOY_INTENT.search(text):
        intent = "deploy"
    elif REMINDER_INTENT.search(text):
        intent = "reminder"
    elif RESEARCH_INTENT.search(text):
        intent = "research"
    elif TASK_INTENT.search(text) or ACTION_VERBS.search(text):
        intent = "task"
    else:
        intent = "question" if "?" in text else "task"

    if HIGH_RISK_SCOPE.search(text) or intent in {"deploy", "incident"}:
        risk = "high"
    elif HIGH_RISK_ACTION.search(text) or MEDIUM_RISK_SCOPE.search(text):
        risk = "medium"
    else:
        risk = "low"

    semantic_trackable = bool(
        trackable
        or (
            intent in {"task", "research", "reminder"}
            and action_count > 0
            and (score >= 3 or WORK_NOUNS.search(text) or DURABLE_OUTPUT.search(text))
        )
    )

    if intent == "question":
        execution = "no_dispatch"
        initial_status = "none"
        reason = "Question simple: pas de carte Kanban ni dispatch automatique."
    elif risk == "high":
        execution = "needs_human"
        initial_status = "blocked"
        reason = "Risque élevé: qualification et validation humaine requises."
    elif risk == "medium":
        execution = "needs_human"
        initial_status = "blocked"
        reason = "Risque moyen: tâche conservée en Kanban avant dispatch contrôlé."
    else:
        execution = "auto_dispatch_allowed"
        initial_status = "ready" if DEFAULT_READY_LOW_RISK else "blocked"
        reason = (
            "Tâche low-risk assez cadrée: prête pour dispatch contrôlé."
            if DEFAULT_READY_LOW_RISK
            else "Tâche low-risk conservée à qualifier par configuration."
        )

    return {
        "intent": intent,
        "risk": risk,
        "execution": execution,
        "initial_status": initial_status,
        "trackable": bool(semantic_trackable and execution != "no_dispatch"),
        "score": score,
        "action_count": action_count,
        "reason": reason,
    }


def is_trackable(message: str) -> bool:
    return bool(classify_message(message)["trackable"])


def project_for(message: str) -> str:
    text = message.lower()
    if "cpanel" in text or "lws" in text or "blocksdevs" in text:
        return "infrastructure-cpanel-lws"
    if "vps117293" in text or "vps principal" in text:
        return "infrastructure-vps"
    if any(
        token in text
        for token in (
            "hermes",
            "workspace",
            "mcp",
            "sarl-agent-ai",
            "stack",
            "telegram",
        )
    ):
        return "sarl-agent-ai"
    domains = re.findall(r"\b[a-z0-9-]+\.(?:com|net|org|fr|ci)\b", text)
    return domains[0] if domains else "operations"


def title_for(message: str) -> str:
    cleaned = normalize(re.sub(r"```[\s\S]*?```", " ", message))
    first = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0]
    if len(first) > 92:
        first = first[:89].rstrip() + "..."
    return f"Telegram · {first or 'Mission sans titre'}"


def load_index() -> dict:
    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("version", 1)
            data.setdefault("processed", {})
            data.setdefault("ignored", [])
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"version": 1, "processed": {}, "ignored": []}


def save_index(index: dict) -> None:
    tmp = INDEX_FILE.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, INDEX_FILE)


def telegram_messages() -> list[sqlite3.Row]:
    connection = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(
            """
            SELECT m.id, m.session_id, m.timestamp, m.content, s.user_id
            FROM messages AS m
            JOIN sessions AS s ON s.id = m.session_id
            WHERE s.source = 'telegram'
              AND m.role = 'user'
              AND coalesce(m.content, '') <> ''
            ORDER BY m.id
            """
        ).fetchall()
    finally:
        connection.close()


def create_card(row: sqlite3.Row) -> tuple[str, dict[str, str | int | bool]]:
    message = str(row["content"])
    project = project_for(message)
    classification = classify_message(message)
    timestamp = datetime.fromtimestamp(
        float(row["timestamp"]), tz=timezone.utc
    ).isoformat()
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]
    body = "\n".join(
        (
            "Source: Telegram",
            "Statut d'import: à qualifier",
            f"Projet détecté: {project}",
            "",
            "Classification:",
            f"- intent: {classification['intent']}",
            f"- risk: {classification['risk']}",
            f"- execution: {classification['execution']}",
            f"- initial_status: {classification['initial_status']}",
            f"- score: {classification['score']}",
            f"- reason: {classification['reason']}",
            "",
            f"Session: {row['session_id']}",
            f"Message: {row['id']}",
            f"Date: {timestamp}",
            "",
            "Demande:",
            message.strip(),
        )
    )
    command = [
        HERMES_BIN,
        "kanban",
        "--board",
        BOARD,
        "create",
        title_for(message),
        "--body",
        body,
        "--initial-status",
        str(classification["initial_status"]),
        "--tenant",
        project,
        "--created-by",
        "telegram-sync",
        "--idempotency-key",
        f"telegram-message:{row['id']}:{digest}",
        "--json",
    ]
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "HERMES_HOME": str(HERMES_HOME)},
    )
    payload = json.loads(completed.stdout)
    task_id = payload.get("id") or payload.get("task", {}).get("id")
    if not task_id:
        raise RuntimeError(f"Kanban create returned no task id: {completed.stdout}")
    return str(task_id), classification


def send_telegram_ack(
    row: sqlite3.Row,
    task_id: str,
    project: str,
    classification: dict[str, str | int | bool],
) -> dict[str, str | bool | int | None]:
    if not TELEGRAM_SYNC_NOTIFY:
        return {"sent": False, "reason": "disabled"}

    chat_id = str(row["user_id"] or "").strip()
    target = f"telegram:{chat_id}" if chat_id else "telegram"
    status = str(classification["initial_status"])
    message = "\n".join(
        (
            "Hermes a créé une carte Kanban depuis ton message Telegram.",
            "",
            f"- task_id: {task_id}",
            f"- projet: {project}",
            f"- statut: {status}",
            f"- intent: {classification['intent']}",
            f"- risk: {classification['risk']}",
            f"- execution: {classification['execution']}",
            "",
            (
                "Validation humaine requise avant dispatch."
                if classification["execution"] == "needs_human"
                else "Tâche prête pour dispatch contrôlé."
            ),
        )
    )
    completed = subprocess.run(
        [HERMES_BIN, "send", "--to", target, "--quiet", message],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "HERMES_HOME": str(HERMES_HOME)},
    )
    return {
        "sent": completed.returncode == 0,
        "target": target,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip()[:500] or None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ignore-message-id",
        type=int,
        action="append",
        default=[],
        help="Mark a Telegram message as intentionally excluded.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not STATE_DB.exists():
        raise SystemExit(f"Missing Hermes state database: {STATE_DB}")

    index = load_index()
    ignored = {int(value) for value in index.get("ignored", [])}
    ignored.update(args.ignore_message_id)
    index["ignored"] = sorted(ignored)
    processed = index["processed"]

    created = 0
    skipped = 0
    for row in telegram_messages():
        message_id = int(row["id"])
        key = str(message_id)
        if key in processed or message_id in ignored:
            continue
        message = str(row["content"])
        classification = classify_message(message)
        if not classification["trackable"]:
            processed[key] = {"trackable": False, "classification": classification}
            skipped += 1
            continue
        if args.dry_run:
            print(
                "TRACK "
                f"{message_id}: [{classification['intent']}/"
                f"{classification['risk']}/"
                f"{classification['execution']}/"
                f"{classification['initial_status']}] {title_for(message)}"
            )
            continue
        project = project_for(message)
        task_id, classification = create_card(row)
        notification = send_telegram_ack(row, task_id, project, classification)
        processed[key] = {
            "trackable": True,
            "taskId": task_id,
            "classification": classification,
            "notification": notification,
            "syncedAt": datetime.now(timezone.utc).isoformat(),
        }
        save_index(index)
        created += 1

    if not args.dry_run:
        save_index(index)
    print(
        json.dumps(
            {
                "ok": True,
                "created": created,
                "skipped": skipped,
                "processed": len(processed),
                "ignored": sorted(ignored),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(error.stderr or str(error), file=sys.stderr)
        raise
