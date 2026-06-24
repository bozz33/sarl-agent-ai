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
  └── sarl-orchestrator
      ├── code-builder / codex-builder
      ├── code-reviewer / code-reviewer-critical
      ├── research-sage / docs-scribe
      ├── ops-foundation / cpanel-watch-agent
      ├── community-manager / support-agent
      ├── designer-3d-agent / bureau-etudes-agent
      └── qa-agent / sarl-governor
```

Profile = identite permanente. Swarm = coordination live. Kanban = travail
durable. Aucun worker ne demarre automatiquement.

## Central Orchestrator Pattern

Le systeme utilise un orchestrateur central unique: `sarl-orchestrator`.

Les domaines ne disposent pas d'orchestrateurs permanents. Les domaines sont representes par des skills de module et des agents specialises.

```text
Entrees
  -> sarl-router
    -> sarl-orchestrator
      -> skills de module
        -> agents specialises
          -> Kanban / Swarm / QA / Governor / memoire MCP
```

Regles structurantes:

- `sarl-orchestrator` decide, decompose, delegue, suit et consolide.
- Les agents specialises executent dans leur domaine.
- `sarl-governor` verifie risques, couts, validations et actions interdites.
- Kanban conserve la trace durable.
- Swarm coordonne les missions complexes.
- MCP memoire conserve uniquement les apprentissages durables valides.
- Telegram est une inbox intelligente, pas un moteur d'execution directe.

## Multi-modeles

Oui, plusieurs modeles/fournisseurs peuvent etre utilises.

OpenRouter est retire de la configuration active SARL-Agent-AI. Les fournisseurs/modeles actifs cibles sont Claude, GPT, Codex, Opus, DeepSeek et Gemini.

Recommandation:

```text
Pre-triage:
  Gemini Flash ou DeepSeek.

Orchestrateur central:
  GPT ou Claude.

Execution courante:
  Gemini ou DeepSeek.

Documentation et recherche simple:
  Gemini.

Code avance:
  Codex uniquement via codex-builder.

Review critique:
  GPT ou Claude.

Analyse exceptionnelle:
  Opus uniquement avec validation humaine.
```

Regles de cout et securite:

- Ne jamais appeler Opus automatiquement.
- Ne jamais utiliser Codex comme orchestrateur general.
- Ne jamais utiliser GPT/Claude pour un simple resume si Gemini/DeepSeek suffit.
- Utiliser Codex seulement pour code avance.
- Utiliser Opus seulement apres validation ou justification exceptionnelle.

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
- Pas de Codex comme orchestrateur.
- Pas d'Opus en usage automatique quotidien.
- Pas d'OpenRouter dans la configuration active.
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
