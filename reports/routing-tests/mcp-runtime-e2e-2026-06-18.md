# MCP memoire runtime E2E - 18 juin 2026

## Runtime

```text
image: sarl/project-memory-mcp:0.1.1
etat: healthy
port hote publie: aucun
PostgreSQL: socket Unix local
pgvector: 0.6.0
```

## Profiles connectes

```text
sarl-router
sarl-orchestrator
sarl-orchestrator-critical
research-sage
docs-scribe
```

Chaque profil decouvre 8 outils.

## Tests

1. `project_memory_write` par `sarl-orchestrator`.
2. `project_memory_search` direct : resultat trouve.
3. Recherche par agent : `MCP_MEMORY_E2E_OK`.
4. Projet hors allowlist : `MCP_ISOLATION_OK`.
5. Nettoyage final :

```text
projects=0
memory=0
chunks=0
```

## Incident corrige

Image 0.1.0 contenait une requete SQL sans casts explicites sur parametres
optionnels. PostgreSQL retournait `could not determine data type of parameter
$3`. Correction ajoutee, image 0.1.1 reconstruite et seul conteneur MCP
recree.
