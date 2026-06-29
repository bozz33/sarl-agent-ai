# DELIVERY.md — flowguard

## Environnements
- dev (docker-compose.dev.yml)
- prod

## Déploiement
- Image via `make docker-build`. Aucun deploy auto sans validation humaine.
- flowguard = composant sécurité (auth/RBAC/mTLS) : tout changement de comportement réseau = validation humaine obligatoire.

## Rollback
- Repartir du tag/commit précédent + image précédente.
- Vérifier qu'aucune migration de config (policy/rbac) n'est irréversible avant de basculer.

## Checklist avant livraison
- `make validate` OK
- e2e suites sensibles OK
- review + review critique (auth/réseau) OK
- diff de config policy/rbac/jwt relu
- rollback connu (image + config précédentes)
- validation humaine obtenue
