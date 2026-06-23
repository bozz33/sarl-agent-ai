# Patch d'activation memoire

Non applique.

Actions soumises a validation :

1. inserer la regle dediee dans `/etc/postgresql/16/main/pg_hba.conf` ;
2. recharger PostgreSQL, sans restart ;
3. ajouter `project-memory-mcp` a `docker-compose.yml` ;
4. lancer uniquement ce nouveau service ;
5. ajouter le MCP HTTP interne aux cinq profiles :

```bash
hermes -p sarl-router mcp add sarl_project_memory \
  --url http://project-memory-mcp:8000/mcp
hermes -p sarl-orchestrator mcp add sarl_project_memory \
  --url http://project-memory-mcp:8000/mcp
hermes -p sarl-orchestrator-critical mcp add sarl_project_memory \
  --url http://project-memory-mcp:8000/mcp
hermes -p research-sage mcp add sarl_project_memory \
  --url http://project-memory-mcp:8000/mcp
hermes -p docs-scribe mcp add sarl_project_memory \
  --url http://project-memory-mcp:8000/mcp
```

6. tester protocole MCP et isolation projet ;
7. confirmer qu'aucun port n'est publie ;
8. confirmer que les services Hermes existants n'ont pas redemarre.

Rollback :

1. retirer les entrees MCP des profiles ;
2. arreter et retirer seulement `sarl-project-memory-mcp` ;
3. retirer le service Compose ;
4. retirer la ligne `pg_hba.conf` et recharger PostgreSQL ;
5. conserver base et secret pour diagnostic, ou les supprimer seulement apres
   validation destructive distincte.
