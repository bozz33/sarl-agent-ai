---
name: sarl-trading-self-improvement
description: Encadrer l'amélioration du module trading. Autorise propositions, tâches Kanban et rapports sans validation ; interdit toute modification de règle active, hausse de risque, ajout de marché ou activation live sans validation humaine.
---

# Skill — sarl-trading-self-improvement

## Objectif

Permettre au module d'apprendre et de proposer des améliorations, tout en
gardant l'humain dans la boucle pour tout changement sensible.

## Quand utiliser

Après analyse de backtests/résultats, lors des revues hebdomadaires.

## Autorisé sans validation

proposer une amélioration · ouvrir une tâche Kanban · produire un rapport ·
écrire une leçon non sensible en mémoire · produire des statistiques.

## Interdit sans validation humaine

modifier une règle de risque active · augmenter le risque · ajouter un marché ·
modifier une skill active · activer un chemin live · modifier le wrapper d'ordre.

## Format de proposition

```
LEARNING_PROPOSAL:
SOURCE_BACKTEST_ID:
OBSERVATION:
PROPOSAL:
EXPECTED_EFFECT:
RISK_REVIEW:
GOVERNOR_STATUS:
HUMAN_VALIDATION_REQUIRED: yes
```

Toute proposition validée est tracée dans `learning_proposals` (journal) avant
toute application.
