# AGENTS.md — flowguard

Contexte agent SARL. NE PAS commiter dans le repo flowguard. Vit côté SARL.

## Projet
- Nom : flowguard
- Repo source : `/root/CascadeProjects/flowguard`
- Module : `github.com/bozz33/flowguard`
- Type : service Go (proxy/gateway, RBAC/JWT/OIDC/mTLS/policy)
- Stack : **Go 1.26.4**, Docker, docker-compose (suites par feature)
- État : en prod

## Commandes (depuis /root/CascadeProjects/flowguard)
- Install/deps : `go mod download`
- Format : `make fmt`  / check : `make fmt-check`
- Vet : `make vet`
- Tests : `make test`
- Tests race : `make test-race`
- Bench : `make bench`
- **Gate complet : `make validate`** (= fmt-check + vet + test + test-race)
- Build image : `make docker-build`
- Build bin : `go build ./...`
- E2E par feature : `make validate-<suite>` (jwt-auth, oidc-jwks, rbac, policy-engine, mtls, observability, tracing, discovery, priority-failover, weighted-round-robin, mtls, soak, endurance…) — chaque cible lance un docker-compose dédié.

## Règles
- Toujours `make validate` avant de proposer un merge.
- Pas de merge main / deploy sans validation humaine.
- Checkpoint + branche/worktree avant modif.
- Suite e2e pertinente si la zone touchée a un `validate-*` correspondant.
