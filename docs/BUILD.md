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
patches SARL (suppression du SSE global, suivi borné, etc.). Ni le Dockerfile ni
le jeu de patches ne sont versionnés ici.

**Risque** : perte de l'image = pas de reconstruction possible sans refaire les
patches à la main.

**Action recommandée** : versionner le jeu de patches (diff vs `d04e1f3`) sous
`deploy/hermes-workspace/` + un Dockerfile, OU figer une image publiée dans un
registre. Voir aussi `docs/ROSTER.md` pour la reproductibilité globale.

## Sandbox

`docker:27-dind` est tiré par digest SHA (pas de build local), volontaire.
