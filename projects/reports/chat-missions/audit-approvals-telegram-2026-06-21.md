# Audit approbations, suivi chat et Telegram

- Source : conversation opérateur
- Statut : terminé
- Date : 2026-06-21

## Correctifs appliqués

- flux d’approbation du chat raccordé aux événements `approval.request` ;
- boutons Approve/Deny raccordés à l’API `/v1/runs/{run_id}/approval` ;
- faux positif du garde `.secrets` corrigé pour les tests négatifs d’exposition ;
- healthcheck adapté aux rapports de missions créés automatiquement ;
- Telegram configuré sur un seul utilisateur et un seul chat ;
- accès global aux plateformes désactivé ;
- anciennes copies de jetons Telegram expurgées des artefacts texte ;
- image Workspace déployée : `sarl/hermes-workspace:d04e1f3-sarl9-approvals`.

## Validation

- services Docker sains ;
- healthcheck complet réussi ;
- 9 tests du garde de sécurité réussis ;
- 20 tests Workspace ciblés réussis ;
- build client et SSR réussi ;
- endpoint d’approbation authentifié et correctement proxifié ;
- Telegram connecté en polling et message de test envoyé.

## Limites restantes

- le dépôt Workspace upstream contient des erreurs TypeScript globales préexistantes ;
- les tests Vitest laissent parfois un processus auxiliaire ouvert pendant dix secondes ;
- les images et caches Docker occupent plusieurs gigaoctets récupérables ;
- une rotation du jeton Telegram reste recommandée puisqu’il a été communiqué en clair.
