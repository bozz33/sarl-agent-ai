# Centralisation Workspace — 21 juin 2026

## Résultat

- Workspace Tasks utilise exclusivement le Kanban Hermes partagé.
- Les missions importantes du chat Workspace continuent d'être suivies.
- Les missions importantes Telegram sont synchronisées chaque minute.
- Les imports Telegram sont créés en `blocked` et exigent une revue humaine.
- Les jobs sont agrégés depuis tous les profils Hermes.
- Les MCP configurés dans les profils autorisés sont visibles dans Workspace en
  lecture seule.
- Le profil `default` ne reçoit aucun serveur MCP.
- Le CRUD email/cPanel reste hors périmètre.

## Runtime

- Image Workspace :
  `sarl/hermes-workspace:d04e1f3-sarl11-centralized`
- Timer :
  `sarl-agent-ai-telegram-work-sync.timer`
- Board :
  `sarl-agent-ai`

## Import Telegram initial

Trois missions historiques ont été retenues :

- `t_5b3a8d89` — surveillance des deux serveurs ;
- `t_5fdc0956` — analyse des sept sites ;
- `t_8145b079` — supervision quotidienne détaillée.

Elles sont toutes en `blocked`, sans worker actif, avec une étiquette projet.
Le message relatif au CRUD email est explicitement ignoré.

## MCP

Workspace retourne le mode `profiles` :

- serveur : `sarl_project_memory` ;
- profils autorisés : 17 ;
- lecture seule dans Workspace ;
- `default.mcp_servers` : absent.

## Jobs

Deux jobs sont visibles dans Workspace :

- `sarl-weekly-stack-audit` — profil `sarl-stack-steward` ;
- `sarl-weekly-governance-audit` — profil `sarl-governor`.

## Sécurité

Le premier essai d'import en `triage` a déclenché le décomposeur automatique
Hermes. Les workers générés ont été arrêtés, leurs cartes archivées et le
synchroniseur a été corrigé pour utiliser directement `blocked`. La
vérification finale confirme qu'aucun worker Kanban n'est actif.

## Validation

- 65 tests Workspace ciblés réussis ;
- build client et SSR réussi ;
- healthcheck global réussi ;
- Agent, Workspace et MCP sains ;
- Telegram connecté ;
- timer activé ;
- API MCP, Jobs et Tasks authentifiées vérifiées.
