---
name: sarl-self-improvement
description: Guider l'orchestrateur central pour PROPOSER des améliorations de skills, SOUL et procédures à partir des rapports et de la mémoire, sans jamais les appliquer sans sandbox, governor et validation humaine.
---

# Skill — sarl-self-improvement

## Objectif

Permettre au système de s'améliorer **sous supervision stricte**. L'agent analyse
les missions passées, les rapports et la mémoire projet, puis **propose** des
améliorations de skills, de SOUL ou de procédures. Il ne les applique jamais
directement.

Règle absolue :

```text
PROPOSER, jamais APPLIQUER.
Aucune modification de skill, SOUL, config, swarm ou script sans :
sandbox -> governor -> validation humaine -> merge.
```

## Quand utiliser

- Mission récurrente `weekly-self-improvement-review`.
- Après un incident confirmé ou une erreur récurrente.
- Quand la mémoire projet révèle une procédure défaillante ou améliorable.
- Quand un rapport (ops, coût, support, gouvernance) signale un écart répétable.

## Entrées nécessaires

- Rapports récents (cpanel, coût, kanban, gouvernance) injectés par le collecteur.
- Mémoire projet (`project_memory_search`, `project_memory_summary`,
  `project_memory_decision_log`).
- État courant des skills/SOUL concernés.

## Workflow

1. Lire les rapports récents et la mémoire projet.
2. Identifier un problème RÉEL et RÉPÉTABLE (pas une intuition ponctuelle).
3. Distinguer FAIT, INFERENCE, INCONNU.
4. Formuler une proposition d'amélioration ciblée (1 problème = 1 proposition).
5. Écrire la proposition dans
   `knowledge/improvement-proposals/<date>-<slug>.md` (NE PAS modifier le skill
   ou le SOUL cible).
6. Classer le risque et marquer `VALIDATION_HUMAINE_REQUISE: oui`.
7. Notifier (Telegram) avec un résumé bref et la demande de validation.
8. Écrire en mémoire uniquement le problème confirmé, pas la proposition.

## Actions autorisées

- lire rapports, mémoire, skills, SOUL ;
- rédiger une proposition d'amélioration en fichier dédié ;
- citer des preuves (rapport, run, date) ;
- proposer un patch sous forme de diff lisible commenté.

## Actions interdites sans validation humaine

- modifier un skill, un SOUL, `swarm.yaml`, une config profil ou un script ;
- appliquer un patch ;
- créer/supprimer un profil ou un agent ;
- changer un modèle ou un fournisseur ;
- toute action production, cPanel, DNS, SSL, secrets, base de données ;
- merge sur une branche.

## Gouvernance

- `sarl-governor` vérifie chaque proposition (risque, coût, conformité
  architecture, respect des interdits).
- L'application d'une proposition validée se fait hors agent, en sandbox/worktree,
  avec tests, puis revue et merge humain (voir `scripts/apply-skill-proposal.sh`).

## Format de proposition (fichier)

```text
PROPOSITION_AMELIORATION:
ID:
DATE:
CIBLE:            (skill / SOUL / procédure / script — chemin exact)
PROBLEME_CONFIRME:
PREUVES:          (rapport, run, date)
CHANGEMENT_PROPOSE:
DIFF_PROPOSE:     (extrait lisible, non applique)
BENEFICE_ATTENDU:
RISQUE:
TESTS_RECOMMANDES:
VALIDATION_HUMAINE_REQUISE: oui
```

## Rapport final (Telegram)

```text
RAPPORT_AMELIORATION:
PERIODE:
PROBLEMES_DETECTES:
PROPOSITIONS_ECRITES:   (chemins des fichiers)
TOP_PRIORITE:
RISQUE:
VALIDATION_HUMAINE_REQUISE: oui
PROCHAINE_ACTION:       (revue humaine + apply-skill-proposal.sh)
```
