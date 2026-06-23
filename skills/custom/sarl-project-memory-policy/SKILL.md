---
name: sarl-project-memory-policy
description: Regles d'isolation et de qualite de la memoire projet SARL.
---

# Project Memory Policy

1. Toute entree possede un `project_id`.
2. Toute decision utilise `truth_status=decision`.
3. Toute hypothese utilise `truth_status=hypothesis`.
4. Une information obsolete devient `deprecated` ou `superseded`.
5. Ne jamais indexer secrets, `.env`, tokens ou donnees sensibles non autorisees.
6. Stocker gros fichiers sur disque; memoire conserve chemin, empreinte et metadonnees.
7. Citer source et niveau de confiance.
8. Ne jamais lire ou ecrire dans la memoire d'un autre projet.

