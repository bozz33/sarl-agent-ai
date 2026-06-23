---
name: sarl-human-validation
description: Politique de validation humaine obligatoire pour actions critiques.
---

# Human Validation

Validation explicite obligatoire avant :

- changement Docker Compose ou image ;
- modification `.env` ou `.secrets` ;
- migration ou suppression PostgreSQL ;
- suppression de donnees ;
- deploiement production ;
- modification DNS, pare-feu ou reverse proxy ;
- publication officielle ou envoi client final ;
- action financiere ou juridique.

## Demande

```text
ACTION_DEMANDEE:
PROJET:
POURQUOI:
RISQUES:
BACKUP_EXISTANT:
ROLLBACK:
TESTS:
VALIDATION_REQUISE:
```

