# Crons, approbations, vidéos et suivi sélectif — 2026-06-21

## Résultat

- Les crons de maintenance restent en `cron_mode: deny` comme barrière de
  sécurité finale, mais ils ne tentent plus d'exécuter une opération critique.
- Ils produisent une proposition durable : preuves, patch ou commandes exactes,
  impact, sauvegarde, tests et rollback.
- Une proposition importante est contrôlée par `sarl-governor`, enregistrée en
  Kanban `review` et envoyée sur Telegram sous la forme
  `APPROBATION_REQUISE: <task_id>`.
- Après approbation humaine portant sur cet identifiant, une nouvelle session
  `ops-foundation` reprend uniquement le périmètre validé.
- Les constats mineurs ne créent pas de tâche.

## Crons actifs

- `782531781371` — audit hebdomadaire de la stack, lundi 06:00 UTC, livraison
  Telegram.
- `b6d629c0ec37` — audit hebdomadaire de gouvernance, lundi 07:30 UTC,
  livraison Telegram.

Prochaine exécution prévue : lundi 22 juin 2026.

## Suivi sélectif des conversations

Le Workspace utilise maintenant un score d'importance. Sont suivis les travaux
substantiels concernant notamment un projet, la plateforme, la production,
la sécurité, un déploiement, une migration, une automatisation, un audit,
plusieurs actions ou un livrable durable.

Restent uniquement dans le chat : questions, salutations, petits résumés,
petites rédactions et actions triviales. Une demande explicite de créer ou
suivre une tâche reste prioritaire.

Validation automatisée : 21 tests réussis.

## Revue des vidéos

YouTube refuse depuis l'adresse IP du serveur l'accès automatisé aux flux et
aux transcriptions avec une vérification anti-bot. Les titres et auteurs ont pu
être vérifiés, mais le contenu intégral n'a pas pu être visionné ou transcrit.
Les conclusions suivantes sont donc des axes déduits des métadonnées, et non
une validation détaillée de chaque démonstration.

Thèmes récurrents :

- installation et maîtrise de Hermes ;
- agent orchestrateur et équipes multi-agents ;
- Hermes Workspace et agents permanents ;
- automatisation métier ;
- erreurs d'installation et d'adoption ;
- équipe de sécurité spécialisée ;
- exploitation économique sur serveur.

## Apports retenus pour SARL-Agent-AI

1. Conserver un orchestrateur qui délègue à des profils spécialisés plutôt
   qu'un agent omnipotent.
2. Séparer strictement audit, gouvernance et exécution.
3. Utiliser des états durables Kanban pour survivre aux fins de session et aux
   redémarrages.
4. Réserver les agents permanents aux contrôles périodiques importants.
5. Exiger preuve, portée, risque, backup, tests et rollback avant toute
   approbation.
6. Mesurer les coûts et éviter qu'une conversation ordinaire déclenche une
   mission persistante.
7. Employer un profil sécurité spécialisé pour l'analyse, sans lui donner une
   autorisation implicite d'exécuter des opérations offensives ou destructives.

## Vérifications de production

- Image Workspace :
  `sarl/hermes-workspace:d04e1f3-sarl10-selective-tracking`.
- Agent Hermes : sain.
- Workspace : sain.
- Mémoire projet : saine.
- Telegram : connecté.
- Contrôle global `scripts/healthcheck.sh` : réussi.

## Limite restante

Le protocole d'approbation différée repose sur un message explicite comportant
le `task_id`. L'approbation dans le chat Workspace peut utiliser l'interface
d'approbation intégrée ; sur Telegram, la validation est textuelle et doit
mentionner l'identifiant. Aucun changement hors du périmètre de cette tâche ne
doit être exécuté.
