# SARL Project Memory MCP

Service MCP Python pour memoire metier isolee par `project_id`.

Etat : service 0.1.2 actif. PostgreSQL, pgvector 0.6.0, role/base dedies,
migration, connexion MCP et tests d'integration sont valides.

La version 0.1.2 partage un pool PostgreSQL unique entre les sessions HTTP
MCP. Elle corrige l'accumulation de plusieurs connexions idle par reconnexion
de profil, qui pouvait epuiser `max_connections`.

## Garanties

- `project_id` obligatoire et allowlist stricte ;
- requetes SQL parametrees ;
- decisions et hypotheses forcees vers leur `truth_status` correct ;
- contenu et chemins ressemblant a des secrets refuses ;
- memoires obsoletes marquees `deprecated` ou `superseded`, pas supprimees ;
- recherche lexicale disponible avant activation des embeddings ;
- colonne pgvector sans dimension fixe tant que le modele d'embedding cible
  n'est pas valide.

## Outils

```text
project_context_get
project_memory_search
project_memory_write
project_memory_decision_log
project_memory_summary
project_memory_supersede
project_memory_list_recent
project_memory_get
```

## Installation de developpement

```bash
cd /root/CascadeProjects/SARL-agent-ai/services/project-memory-mcp
uv sync
cp .env.example .env
```

Ne pas renseigner de secret dans Git.

## Tests

```bash
python -m unittest discover -s tests -v
```

Le test PostgreSQL complet utilise `SARL_MEMORY_TEST_DATABASE_URL`. Il cree une
fixture temporaire, valide ecriture/recherche/lecture/supersession puis nettoie
les tables.

## Activation DB realisee

L'activation exige :

1. backup PostgreSQL ;
2. installation pgvector ;
3. creation user/base dedies ;
4. application de `migrations/001_init.sql` ;
5. tests d'isolation projet ;
6. configuration MCP Hermes ;
7. rollback documente.

Ces actions ont ete realisees apres backup et validation humaine.

## Architecture runtime preparee

```text
Hermes Agent
  -> HTTP MCP interne
project-memory-mcp:8000/mcp
  -> socket Unix montee
/var/run/postgresql/.s.PGSQL.5432
  -> PostgreSQL hote
```

Aucun port MCP ou PostgreSQL ne doit etre publie sur l'hote ou Internet.

Les embeddings semantiques restent explicitement desactives tant qu'aucun
modele, aucune dimension et aucun budget n'ont ete approuves. La recherche
lexicale isolee par `project_id` est operationnelle.
