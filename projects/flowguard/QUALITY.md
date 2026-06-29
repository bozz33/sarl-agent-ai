# QUALITY.md — flowguard

## Gates obligatoires
- `make fmt-check` (format)
- `make vet`
- `make test`
- `make test-race`  (Go = détection data races critique pour un proxy concurrent)
- `make validate-<suite>` si la feature touchée a une suite e2e dédiée
- Review standard (code-reviewer / deepseek-reasoner)
- Review critique (code-reviewer-critical / Claude) si : auth, RBAC, JWT/OIDC, mTLS, policy, ou chemin réseau exposé

## Définition de terminé
Tâche terminée seulement si :
- `make validate` passe (vert) ;
- e2e pertinent passe si zone sensible ;
- rapport produit ;
- review faite ;
- risques sécurité documentés (flowguard = composant de sécurité réseau) ;
- validation humaine demandée si auth/réseau/prod.
