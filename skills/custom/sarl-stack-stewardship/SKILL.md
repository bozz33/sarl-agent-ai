---
name: sarl-stack-stewardship
description: Maintenance supervisee de la stack Hermes SARL-Agent-AI.
---

# Stack Stewardship

Autorise sans validation :

- lire documentation officielle ;
- auditer configuration ;
- produire rapport ;
- preparer patch dans `staging/` ;
- executer test non destructif.

Interdit sans validation :

- `docker compose pull`, `down`, `restart` ou changement Compose ;
- modification secrets ;
- installation systeme ;
- migration DB ;
- suppression ;
- exposition publique.

Toujours fournir backup, rollback, tests et impact.

