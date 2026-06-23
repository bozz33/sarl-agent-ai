# Politique memoire projet

- Memoire native Hermes : etat propre au profil.
- Memoire metier : PostgreSQL + pgvector via MCP.
- Toute entree metier possede `project_id`, `type` et `truth_status`.
- Aucun secret ou fichier `.env` indexe.
- Gros fichiers sur disque; DB conserve chemin, empreinte et fragments.
- Code MCP, image, pgvector, base dediee et migration valides.
- 12 tests unitaires et 1 test PostgreSQL valides.
- Base vide : aucun projet ni contenu metier cree.
- Configuration MCP Hermes active sur les dix-sept profils.
- Recherche hybride lexicale + Gemini `gemini-embedding-001` en 768
  dimensions, avec repli lexical automatique si le provider est indisponible.
