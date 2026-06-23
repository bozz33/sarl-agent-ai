# Activation memoire projet

Etat : prepare, non execute.

## Etat verifie le 18 juin 2026

```text
PostgreSQL: 16.14
Bases utilisateur: postgres uniquement
Extension vector disponible: non
Paquet Ubuntu candidat: postgresql-16-pgvector 0.6.0-1
Version upstream documentee: pgvector 0.8.3
```

Le paquet Ubuntu suffit au schema initial et limite les changements systeme.
Une compilation upstream 0.8.3 ajouterait des dependances et une maintenance
manuelle. Decision recommandee pour ce palier : paquet Ubuntu, puis reevaluation
avant activation des index vectoriels avances.

## Validation humaine requise

Action :

```text
installer postgresql-16-pgvector
creer la base sarl_agent_memory
creer le role sarl_memory_user
appliquer migrations/001_init.sql
```

Risques :

- installation paquet systeme ;
- creation role et base PostgreSQL ;
- migration de schema ;
- nouveau secret DB a stocker ;
- future connexion MCP a PostgreSQL.

## Backup obligatoire

Avant activation :

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "/root/CascadeProjects/SARL-agent-ai/backups/postgres/$STAMP"
sudo -u postgres pg_dumpall --globals-only \
  > "/root/CascadeProjects/SARL-agent-ai/backups/postgres/$STAMP/globals.sql"
sudo -u postgres pg_dump -Fc postgres \
  > "/root/CascadeProjects/SARL-agent-ai/backups/postgres/$STAMP/postgres.dump"
```

Ajouter SHA-256 aux dumps.

## Ordre d'activation

1. Installer `postgresql-16-pgvector`.
2. Verifier `pg_available_extensions`.
3. Generer un mot de passe fort sans l'afficher.
4. Stocker le secret dans `.secrets`, permissions `0600`.
5. Creer role et base dedies.
6. Activer extension `vector` dans `sarl_agent_memory`.
7. Appliquer `services/project-memory-mcp/migrations/001_init.sql`.
8. Creer seulement les projets explicitement valides.
9. Tester contraintes, isolation et refus secrets.
10. Configurer MCP Hermes.
11. Relancer uniquement le composant necessaire apres validation.

## Rollback

Avant donnees reelles :

```text
1. retirer configuration MCP Hermes ;
2. arreter service MCP ;
3. appliquer 001_init.down.sql si conservation DB souhaitee ;
4. sinon supprimer base puis role apres validation explicite ;
5. restaurer dumps si une regression PostgreSQL est constatee.
```

L'extension `vector` ne doit pas etre supprimee automatiquement : elle peut etre
partagee par d'autres bases.
