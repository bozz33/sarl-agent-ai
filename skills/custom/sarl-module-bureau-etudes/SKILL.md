---
name: sarl-module-bureau-etudes
description: Guider sarl-orchestrator pour analyses, synthèses, notes techniques, calculs préparatoires, dossiers et vérifications de bureau d’études avec validation humaine des livrables engageants.
---

# Skill — sarl-module-bureau-etudes

## Objectif

Gérer les travaux de bureau d’études : analyse, synthèse, notes techniques, calculs et dossiers.

## Quand utiliser

Utiliser cette skill lorsque la demande concerne :
- analyse technique ;
- note de calcul ;
- dimensionnement préparatoire ;
- dossier technique ;
- synthèse réglementaire ;
- vérification documentaire ;
- comparaison de variantes.

## Agents recommandés

- Agent principal : bureau-etudes-agent.
- Recherche : research-sage.
- Documentation : docs-scribe.
- QA : qa-agent.
- Calcul automatisé critique : code-reviewer-critical.

## Entrées nécessaires

Avant de lancer la mission, vérifier :
- projet concerné ;
- discipline ;
- pays ou juridiction ;
- hypothèses ;
- sources ;
- unités ;
- précision attendue ;
- validation humaine requise.

## Workflow

1. Identifier projet, discipline et responsabilité.
2. Consulter AGENTS.md et mémoire projet.
3. Créer une tâche Kanban.
4. Établir entrées, hypothèses et inconnues.
5. Assigner bureau-etudes-agent.
6. Assigner research-sage si source normative nécessaire.
7. Produire note ou synthèse traçable.
8. Demander QA ou review critique pour calcul automatisé.
9. Demander validation humaine pour tout livrable engageant.
10. Produire rapport final.
11. Écrire les apprentissages utiles en mémoire.

## Actions autorisées

- Préparer analyses.
- Synthétiser sources.
- Produire notes préparatoires.
- Comparer variantes.
- Vérifier cohérence documentaire.

## Actions interdites sans validation humaine

- livrable client final ;
- note technique engageante ;
- calcul critique ;
- document réglementaire ;
- décision de construction ou structure ;
- signature ou conformité finale.

## Mémoire projet

Écrire en mémoire uniquement :
- hypothèses validées ;
- méthodes validées ;
- sources durables ;
- décisions techniques confirmées ;
- erreurs récurrentes.

Ne jamais écrire :
- données privées inutiles ;
- secrets ;
- documents clients sensibles non nécessaires.

## Rapport final

Format obligatoire :

RAPPORT_MODULE:
PROJET:
OBJECTIF:
AGENTS_UTILISÉS:
ACTIONS_EFFECTUÉES:
RÉSULTATS:
RISQUES:
VALIDATION_HUMAINE_REQUISE:
MÉMOIRE_MISE_À_JOUR:
PROCHAINE_ACTION:
