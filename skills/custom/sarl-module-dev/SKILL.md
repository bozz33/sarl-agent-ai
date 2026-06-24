---
name: sarl-module-dev
description: Guider sarl-orchestrator pour les missions de développement logiciel, bugs, fonctionnalités, refactor, tests, migrations et revue de code avec délégation vers code-builder, codex-builder, reviewers et QA.
---

# Skill — sarl-module-dev

## Objectif

Gérer les missions de développement logiciel.

## Quand utiliser

Utiliser cette skill lorsque la demande concerne :
- création de fonctionnalités ;
- correction de bugs ;
- refactor ;
- tests ;
- revue de code ;
- documentation technique ;
- migration logicielle.

## Agents recommandés

- Agent principal : code-builder.
- Code avancé : codex-builder.
- Reviewer : code-reviewer.
- Reviewer critique : code-reviewer-critical.
- QA : qa-agent.
- Documentation : docs-scribe.

## Entrées nécessaires

Avant de lancer la mission, vérifier :
- projet concerné ;
- AGENTS.md du projet ;
- branche ou worktree ;
- objectif exact ;
- fichiers ou services concernés ;
- niveau de risque ;
- tests attendus ;
- validation humaine requise ou non.

## Workflow

1. Identifier le projet.
2. Lire AGENTS.md.
3. Consulter la mémoire projet.
4. Vérifier branche ou worktree.
5. Créer checkpoint.
6. Créer une tâche Kanban principale.
7. Décomposer en sous-tâches.
8. Assigner code-builder ou codex-builder selon complexité.
9. Lancer tests adaptés.
10. Demander review.
11. Demander review critique si production, sécurité, base de données ou architecture.
12. Produire patch et rapport.
13. Demander validation avant merge ou déploiement.
14. Écrire les apprentissages utiles en mémoire.

## Actions autorisées

- Lire le code.
- Proposer patch.
- Écrire tests.
- Exécuter tests non destructifs.
- Préparer documentation technique.
- Préparer plan de migration.

## Actions interdites sans validation humaine

- push production ;
- merge main ;
- déploiement ;
- migration base de données ;
- suppression de fichiers ;
- modification secrets ;
- modification infrastructure active ;
- action irréversible.

## Mémoire projet

Écrire en mémoire uniquement :
- décisions techniques validées ;
- bugs confirmés ;
- procédures améliorées ;
- conventions durables ;
- incidents réels.

Ne jamais écrire :
- mots de passe ;
- clés API ;
- tokens ;
- secrets ;
- données privées inutiles.

## Rapport final

Format obligatoire :

RAPPORT_MODULE:
PROJET:
OBJECTIF:
AGENTS_UTILISÉS:
ACTIONS_EFFECTUÉES:
TESTS:
RÉSULTATS:
RISQUES:
VALIDATION_HUMAINE_REQUISE:
MÉMOIRE_MISE_À_JOUR:
PROCHAINE_ACTION:
