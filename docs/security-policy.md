# Politique securite

- Ports Hermes lies a `127.0.0.1`.
- Dashboard `9119` reste interne au reseau Docker.
- Tailscale cible; SSH secours.
- Aucun secret dans Git, projets, rapports ou memoire.
- Validation humaine avant action production, destructive, reseau, DB ou secret.
- Backup et rollback avant changement important.
- Aucun worker ni projet automatique au boot.

