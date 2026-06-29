# AGENTS.md — blocksdevs.com

Contexte agent SARL. NE PAS commiter dans le repo projet. Vit côté SARL.

## Projet
- Nom : blocksdevs.com
- Dir local : `/root/CascadeProjects/blocksdevs.com` = **DEPLOY-ONLY** (juste docker-compose.yml)
- Type : app Node (NODE_ENV=production, PORT 3000)
- Image prod : `bozz33/blocksdev:latest`
- Expose : `127.0.0.1:8082 -> 3000`
- Container : `blocksdev`
- État : en prod

## ⚠️ Code source PAS dans ce dir
Ce dossier ne contient que le compose de déploiement. Le **code source de l'image `bozz33/blocksdev` est ailleurs** (repo séparé / build externe).

AVANT toute tâche de dev :
1. Localiser le repo source (Docker Hub `bozz33/blocksdev`, ou repo GitHub `bozz33/*`).
2. Confirmer la stack exacte (Node + framework) une fois le source trouvé.
3. Compléter ce fichier avec les vraies commandes test/lint/build.

## Commandes (déploiement seul, pour l'instant)
- État : `docker compose ps` / `docker compose logs --tail=100 blocksdev`
- Pull nouvelle image : `docker compose pull && docker compose up -d` (VALIDATION HUMAINE requise)

## Règles
- Pas de pull/redeploy prod sans validation humaine.
- Dev réel impossible tant que le repo source n'est pas localisé — flaguer à l'orchestrateur.
