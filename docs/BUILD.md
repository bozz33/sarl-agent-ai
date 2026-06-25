# Build des images

La stack tourne sur trois images `sarl/*`. Deux sont reconstructibles depuis ce
dépôt, la troisième ne l'est pas encore.

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

## NON reconstructible depuis le repo (gap)

### `sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse`
Build custom de l'upstream `outsourc-e/hermes-workspace` (commit `d04e1f3`) avec
patches SARL (suppression du SSE global, suivi borné, etc.). L'image embarque
uniquement le build (`/app/dist`, `server-entry.js`), **pas les sources** : on ne
peut donc pas régénérer le jeu de patches depuis le conteneur, et l'image n'est
pas publiée dans un registre (pas de digest distant).

**Reprise (DR) — disponible** : `scripts/backup-hermes.sh --with-images` exporte
les images en `.tar` sous `backups/<horodatage>/images/` (tags réels de la stack).
C'est le chemin de survie si le VPS meurt. Restauration : `docker load -i <file.tar>`.

```bash
sudo ./scripts/backup-hermes.sh --consistent --with-images
docker load -i backups/<horodatage>/images/hermes-workspace-image.tar
```

**Source-repro (partiel)** : `deploy/hermes-workspace/` fournit un `Dockerfile`
qui reconstruit une base **vanille** depuis l'upstream au commit épinglé `d04e1f3`
(`docker build -t sarl/hermes-workspace:rebuild deploy/hermes-workspace`). Les
patches SARL (`no-global-sse`, suivi borné) restent à récupérer et à déposer dans
`deploy/hermes-workspace/patches/*.patch` pour reproduire l'image exacte. Détails :
`deploy/hermes-workspace/README.md`. Build volontairement hors compose (évite
d'écraser l'image patchée en prod via `up --build`).

## Sandbox

`docker:27-dind` est tiré par digest SHA (pas de build local), volontaire.
