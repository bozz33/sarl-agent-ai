# DELIVERY.md

Cadre de livraison contrôlée pour SARL-Agent-AI et les projets créés par la
stack.

## Environnements

- local : développement et tests isolés.
- staging : validation humaine et QA avant production lorsque disponible.
- production : jamais modifiée sans accord humain explicite.

## Règles

- Aucun déploiement automatique sans validation humaine.
- Aucun merge sur `main` ou branche protégée sans validation humaine.
- Aucun changement secrets, DNS, SSL, DB, cPanel, email professionnel,
  `public_html`, `.htaccess`, `wp-config.php` ou production sans validation.
- Toute suppression ou action irréversible exige validation humaine.
- Un plan de rollback doit être connu avant livraison.

## Checklist avant livraison

- Contexte projet lu.
- Diff compris et limité.
- Checkpoint, branche ou worktree présent.
- Tests OK ou limites documentées.
- Lint/typecheck/build OK lorsque disponibles.
- E2E OK si interface utilisateur.
- Review standard OK.
- Review critique OK si sensible.
- Backup ou rollback documenté.
- Rapport final produit.
- Validation humaine obtenue pour merge/deploy/action critique.

## Rollback

Le rapport de livraison doit indiquer :

- l'état de départ connu ;
- la commande ou procédure de retour arrière ;
- les données à sauvegarder avant action ;
- les risques résiduels ;
- le point où une validation humaine est requise.
