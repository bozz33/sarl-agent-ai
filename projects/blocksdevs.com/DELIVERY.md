# DELIVERY.md — blocksdevs.com

## Environnements
- prod (container `blocksdev`, image `bozz33/blocksdev:latest`)

## Déploiement
- Update = nouvelle image poussée puis `docker compose pull && up -d`. VALIDATION HUMAINE requise.
- Build de l'image se fait dans le repo source (hors ce dir).

## Rollback
- Re-tag/pull image précédente + `docker compose up -d`.
- Garder le digest de l'image courante avant pull pour pouvoir revenir.

## Checklist avant livraison
- image testée (dans repo source)
- digest courant noté (rollback)
- `docker compose up -d` contrôlé
- site répond sur 8082
- validation humaine obtenue
