# Build des images

La stack tourne sur trois images `sarl/*`, toutes reconstructibles depuis ce dépôt.

## Reconstructible depuis le repo

### `sarl/hermes-agent:0.17.0-ddgs1`
- Dockerfile : `deploy/hermes-agent/Dockerfile`
- Base : `nousresearch/hermes-agent:v2026.6.19` (pin SHA) + `ddgs==9.14.4` (recherche web).
- Build : `docker compose build hermes-agent`

### `sarl/project-memory-mcp:0.2.1`
- Dockerfile : `services/project-memory-mcp/Dockerfile`
- Base : `python:3.12-slim`, install du paquet local (`pyproject.toml` + `src/`).
- Build : `docker compose build project-memory-mcp`

Le câblage `build:` est présent dans `docker-compose.yml`. `docker compose up -d`
réutilise l'image taguée existante ; ajouter `--build` pour reconstruire.

### `sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse`
- Dockerfile + patch : `deploy/hermes-workspace/` (build **hors** compose).
- Source : upstream `outsourc-e/hermes-workspace` au commit `d04e1f3` + le patch
  SARL `patches/sarl13-no-global-sse.patch` (30 fichiers : no-global-sse + suivi
  des missions de chat), récupéré d'une sauvegarde et validé sur upstream vierge.
- Build : `docker build -t sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse deploy/hermes-workspace`

Hors `docker-compose` volontairement : un `up --build` écraserait l'image en prod
sans contrôle. Reconstruire explicitement, tester, retaguer. Détails :
`deploy/hermes-workspace/README.md`.

**Reprise (DR)** : `scripts/backup-hermes.sh --with-images` exporte aussi les images
en `.tar` (tags réels) sous `backups/<horodatage>/images/`. Restauration :
`docker load -i <file.tar>`.

## Sandbox

`docker:27-dind` est tiré par digest SHA (pas de build local), volontaire.
