# SARL-Agent-AI

Stack Hermes Agent + Hermes Workspace, multi-projets et multi-agents.

## Etat

- Hermes Agent et Workspace en Docker Compose.
- Aucun projet ni worker lance automatiquement.
- Dossier projets vide monte sous `/workspace`.
- Skills custom montes en lecture seule.
- Cinq profiles SARL de base configures et testes, arretes par defaut.
- Board Kanban interne et Swarm minimal quatre profils valides.
- PostgreSQL/pgvector et recherche hybride lexicale/semantique actifs.
- MCP memoire 0.2.0 interne, avec pool PostgreSQL partage, embeddings Gemini
  768D et connexion aux dix-sept profils.
- Hook securite, checkpoints et MCP generalises aux dix-sept profils.
- Helper worktree, rollback et restauration isolee des backups valides.
- Sandbox Docker dedie actif avec image Python/Node prechargee; connexion par
  socket Unix prive, aucun port daemon et aucun socket Docker hote expose.
- Six profils avances economiques crees et testes, tous arretes.
- Quatre profils metier crees et testes, sans canal externe.
- Routeur valide 10/10; dix-sept profils valides par appel modele reel.
- Dix-sept profils sont maintenant configurables; les deux profils premium
  utilisent un mode provisoire DeepSeek tant que leurs credentials cibles sont
  absents.
- Crons hebdomadaires governor/stack-steward actifs via timer systemd, sans
  worker profile permanent.
- Workspace utilise le commit officiel `d04e1f3` du 6 juin 2026 avec gzip,
  cache des assets immuables et cache court de la liste des profils. Un
  janitor elimine les watchers PTY de logs dupliques.
- Profils interactifs rapides sur Gemini 3.1 Flash Lite; fallbacks limites et
  timeouts reduits.
- Claude/Codex natifs et Tailscale restent conditionnes par une
  authentification externe; aucun credential n'est invente.

Documentation :

- `docs/SARL-Agent-AI-document-complet-v1.3.md`
- `docs/PHASE2-IMPLEMENTATION.md`
- `ARCHITECTURE.md`

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
