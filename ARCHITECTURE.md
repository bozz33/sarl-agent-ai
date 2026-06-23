# SARL-Agent-AI - Architecture Hermes

## Objectif

Mettre en place une stack VPS propre avec:

- Hermes Agent comme cerveau principal.
- Hermes Workspace comme unique panel d'administration.
- Plusieurs agents Hermes administres depuis Workspace.
- Plusieurs fournisseurs/modeles possibles, sans dependance a Ollama.
- Secrets separes du code et conserves hors depot.

## Sources officielles retenues

- Hermes Agent: https://github.com/NousResearch/hermes-agent
- Documentation Hermes Agent: https://hermes-agent.nousresearch.com/docs/
- Hermes Workspace: https://github.com/outsourc-e/hermes-workspace

## Architecture phase 2

```text
VPS
├── salonducinemaufeminin.net
│   └── stack Docker existante WordPress/MariaDB
│
└── SARL-agent-ai
    ├── docker-compose.yml
    ├── .secrets/
    ├── projects/
    ├── skills/custom/
    ├── services/project-memory-mcp/
    ├── scripts/
    ├── reports/
    ├── staging/
    ├── backups/
    ├── workspace-runtime/
    └── docs/
```

## Services cibles

```text
hermes-agent
  Port interne/expose: 8642
  Role: gateway, chat, modeles, outils, jobs.

hermes-dashboard
  Port interne uniquement: 9119
  Role: config, sessions, skills, jobs, memoire.

hermes-workspace
  Port interne/expose: 3000
  Role: panel unique d'administration.
```

## Principe de connexion

Hermes Workspace doit pointer vers les deux services Hermes:

```env
HERMES_API_URL=http://hermes-agent:8642
HERMES_DASHBOARD_URL=http://hermes-agent:9119
```

Si le gateway utilise une cle API:

```env
HERMES_API_TOKEN=...
```

La meme cle doit etre configuree cote Hermes Agent via `API_SERVER_KEY`.

## Multi-agents cible

Le mode recommande est:

```text
Workspace
  └── Orchestrator Hermes
      ├── Builder agent
      ├── Reviewer agent
      ├── Researcher agent
      ├── Ops agent
      └── QA agent
```

Profile = identite permanente. Swarm = coordination live. Kanban = travail
durable. Aucun worker ne demarre automatiquement.

## Multi-modeles

Oui, plusieurs modeles/fournisseurs peuvent etre utilises.

Hermes Agent annonce officiellement le support de plusieurs fournisseurs: Nous Portal, OpenRouter, NovitaAI, NVIDIA NIM, Hugging Face, OpenAI et endpoints OpenAI-compatible.

Recommandation:

```text
Modele principal orchestrateur:
  Nous Portal ou OpenRouter, modele robuste et rapide.

Modele code/build:
  GPT / OpenAI-compatible / modele fort en code.

Modele recherche:
  modele rapide avec outils web si active.

Modele critique/review:
  modele plus fort, utilise moins souvent.
```

Les changements de modele doivent etre faits via Hermes/Workspace quand possible, pas en bricolant directement les conteneurs.

## Secrets

Ne pas mettre les cles dans Git.

Emplacement local actuel des secrets preserves:

```text
/root/.hermes-secrets-archive/20260617T0035Z
```

Les futurs secrets du projet doivent aller dans:

```text
/root/CascadeProjects/SARL-agent-ai/.secrets/
```

Puis etre montes dans Docker ou injectes via `.env`, selon la documentation officielle.

## Ce qui est volontairement exclu au demarrage

- Pas d'Ollama dans la premiere version.
- Claude et Codex reserves a une phase d'activation dediee.
- Pas de Coolify.
- Pas de Open WebUI.
- Pas de services non necessaires au panel Workspace.

## Etapes phase 2

1. Bind mounts projets et skills.
2. Contextes projets et skills communs.
3. Profiles de base.
4. Routage et fallback.
5. Kanban et Swarm minimal.
6. PostgreSQL + pgvector.
7. MCP memoire Python.
8. Sandbox, worktrees, checkpoints et hooks.
9. Activation Claude/Codex.
