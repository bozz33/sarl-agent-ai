# SARL-Agent-AI

Stack Hermes Agent + Hermes Workspace, multi-projets et multi-agents.

## Etat

- Trois services Docker Compose : `hermes-agent` (0.17.0), `hermes-workspace`
  et `project-memory-mcp` (0.2.1), plus un sandbox Docker-in-Docker isole.
- 19 profils Hermes configures (18 workers Swarm + `sarl-orchestrator-critical`),
  19 SOUL versionnes dans `profiles/`. Voir `docs/ROSTER.md`.
- `sarl-orchestrator` est le cerveau central unique ; les domaines metier sont
  des skills de module, pas des orchestrateurs permanents.
- Kanban durable + Swarm pour les missions complexes ; Governor independant.
- MCP memoire 0.2.1 interne : PostgreSQL/pgvector, embeddings Gemini 768D,
  recherche hybride lexicale/semantique, allowlist `project_id`.
- Securite : hook `pre_tool_call` (policy-guard), checkpoints, redaction des logs,
  secrets hors Git, validation humaine des actions critiques.
- Sandbox DinD : socket Unix prive, reseau interne non routable, aucun port
  daemon expose. Tous les services lies a `127.0.0.1`.
- Crons hebdomadaires governor/stack-steward via timers systemd.
- Telegram = inbox intelligente (classification, Kanban, triage, dispatch controle).

Documentation :

- `docs/ROSTER.md` — alignement swarm / profils / SOUL
- `docs/BUILD.md` — reconstruction des images et reprise (DR)
- `docs/SARL-Agent-AI-document-complet-v1.3.md`
- `docs/PHASE2-IMPLEMENTATION.md`
- `ARCHITECTURE.md`

## Architecture cible

```text
sarl-router
  -> sarl-orchestrator central
    -> skills de module
      -> agents specialises
        -> Kanban / Swarm / QA / Governor / memoire MCP
```

Principes :

- Un seul cerveau central : `sarl-orchestrator`.
- Les modules sont des skills : dev, community, support, ops/cPanel, 3D, bureau d'etudes, research.
- Les agents specialises executent; l'orchestrateur decide et delegue.
- Kanban garde la trace durable.
- Swarm coordonne les missions complexes.
- Governor controle risques, couts, validations et actions interdites.
- Les actions critiques demandent validation humaine.

## Politique modeles

```text
Gemini / DeepSeek -> triage, documentation, recherche simple, execution courante.
GPT / Claude      -> orchestration centrale, arbitrage, review critique.
Codex             -> code avance uniquement.
Opus              -> audit exceptionnel uniquement avec validation.
OpenRouter        -> retire de la configuration active.
```

## Start

```bash
docker compose up -d
```

Workspace local:

```text
http://127.0.0.1:3000
```

## Healthcheck

```bash
sudo ./scripts/healthcheck.sh
```

## Acceptance complete

```bash
sudo ./scripts/acceptance-test.sh
sudo ./scripts/model-workflow-smoke-test.sh
```

## Backup

```bash
sudo ./scripts/backup-hermes.sh --consistent
```

Ajouter `--with-images` pour une sauvegarde autonome des images Docker.

## Licence

MIT — voir `LICENSE`.
