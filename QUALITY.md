# QUALITY.md

Standard qualité obligatoire pour SARL-Agent-AI et les projets créés par la
stack.

## Gates obligatoires

- Tests unitaires ou smoke test ciblé.
- Lint lorsque la stack du projet le fournit.
- Format check lorsque la stack du projet le fournit.
- Typecheck lorsque la stack du projet le fournit.
- Build ou validation équivalente.
- E2E Playwright/Chromium pour toute interface utilisateur.
- Review standard pour tout changement de code.
- Review critique pour sécurité, production, DB, secrets, paiement, migration,
  cPanel, DNS, SSL ou changement irréversible.

## Définition de terminé

Une tâche est terminée uniquement si :

- le contexte projet a été lu ;
- un checkpoint, une branche ou un worktree protège le changement important ;
- les tests applicables passent ou l'impossibilité est documentée ;
- les risques et limites sont documentés ;
- le rapport final est produit ;
- la validation humaine est demandée pour toute action critique.

## Pipeline code

1. Lire la demande et identifier le projet.
2. Lire `AGENTS.md`, `QUALITY.md`, `DELIVERY.md` et `project.yaml`.
3. Consulter mémoire projet et Kanban si disponibles.
4. Créer checkpoint, branche ou worktree avant modification importante.
5. Implémenter le changement avec tests adaptés.
6. Exécuter tests, lint, format check, typecheck, build et e2e applicables.
7. Demander review standard, puis review critique si sensible.
8. Produire rapport final avec commandes exécutées, résultat et risques.
9. Ne jamais merge/deploy sans validation humaine.
