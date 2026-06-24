---
name: sarl-module-support
description: Guider sarl-orchestrator pour support client, triage de tickets, réponses brouillon, incidents, réclamations et escalades sans engagement contractuel automatique.
---

# Skill — sarl-module-support

## Objectif

Traiter support client, triage, réponses et incidents.

## Quand utiliser

Utiliser cette skill lorsque la demande concerne :
- ticket client ;
- demande technique ;
- problème d’accès ;
- incident site ;
- réclamation ;
- demande commerciale simple.

## Agents recommandés

- Agent principal : support-agent.
- Incident technique : ops-foundation.
- Documentation : docs-scribe.
- Governor si sensible : sarl-governor.

## Entrées nécessaires

Avant de lancer la mission, vérifier :
- client ou projet concerné ;
- canal de support ;
- description du problème ;
- impact ;
- urgence ;
- données personnelles impliquées ;
- niveau de risque ;
- validation humaine requise.

## Workflow

1. Identifier projet, client et impact.
2. Consulter AGENTS.md et la mémoire projet.
3. Classifier intention et risque.
4. Créer une tâche Kanban si suivi nécessaire.
5. Assigner support-agent pour triage ou brouillon.
6. Assigner ops-foundation si incident technique.
7. Escalader à sarl-governor si données personnelles, contrat ou risque client.
8. Préparer réponse ou plan d’action.
9. Demander validation humaine si engagement ou action sensible.
10. Produire rapport final.
11. Écrire les apprentissages utiles en mémoire.

## Actions autorisées

- Préparer réponse brouillon.
- Résumer ticket.
- Proposer diagnostic.
- Préparer checklist.
- Créer tâche Kanban.

## Actions interdites sans validation humaine

- remboursement ;
- engagement contractuel ;
- promesse commerciale ;
- modification compte client ;
- suppression données ;
- envoi réponse officielle sensible.

## Mémoire projet

Écrire en mémoire uniquement :
- incidents confirmés ;
- procédures support validées ;
- préférences client durables ;
- erreurs récurrentes.

Ne jamais écrire :
- données personnelles inutiles ;
- secrets ;
- moyens de paiement ;
- informations confidentielles non nécessaires.

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
