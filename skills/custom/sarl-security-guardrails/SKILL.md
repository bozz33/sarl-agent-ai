---
name: sarl-security-guardrails
description: Garde-fous securite pour commandes, fichiers, reseau et donnees SARL.
---

# Security Guardrails

Bloquer ou escalader :

- `rm -rf` sur chemins projet ou systeme ;
- `docker compose down` et changements production ;
- `DROP DATABASE`, `DROP TABLE`, `TRUNCATE` ;
- `chmod 777` et `chown` recursif sur `/root` ;
- lecture ou modification des secrets ;
- ouverture de port public ;
- changement DNS ou reverse proxy ;
- action sans projet identifie.

Redacter tokens et donnees personnelles dans logs et rapports.

