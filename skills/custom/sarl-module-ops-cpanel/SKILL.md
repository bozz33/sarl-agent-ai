---
name: sarl-module-ops-cpanel
description: Guider sarl-orchestrator pour surveillance et diagnostic VPS, cPanel, public_html, WordPress, SSL, emails, logs, disque et fichiers suspects en lecture seule par défaut.
---

# Skill — sarl-module-ops-cpanel

## Objectif

Surveiller et diagnostiquer les serveurs, surtout le cPanel LWS.

## Quand utiliser

Utiliser cette skill lorsque la demande concerne :
- surveillance VPS ;
- surveillance cPanel ;
- public_html ;
- sites web ;
- WordPress ;
- SSL ;
- emails professionnels ;
- logs ;
- espace disque ;
- fichiers suspects.

## Agents recommandés

- Agent principal : ops-foundation.
- cPanel : cpanel-watch-agent.
- Sécurité : security-audit-agent.
- Governor si sensible : sarl-governor.

## Entrées nécessaires

Avant de lancer la mission, vérifier :
- serveur concerné ;
- sites concernés ;
- périmètre lecture seule ;
- accès autorisé ;
- risque ;
- validation humaine requise.

## Workflow

1. Identifier serveur, site et service.
2. Consulter AGENTS.md et mémoire projet.
3. Créer tâche Kanban.
4. Confirmer mode lecture seule par défaut.
5. Assigner ops-foundation ou cpanel-watch-agent.
6. Lire état système, logs autorisés et métriques disponibles.
7. Identifier anomalies, risques et hypothèses.
8. Demander security-audit-agent si fichiers suspects ou incident.
9. Produire rapport.
10. Demander validation humaine avant toute modification.
11. Écrire incidents confirmés ou procédures validées en mémoire.

## Actions autorisées

- lire état système ;
- vérifier services ;
- lire logs autorisés ;
- lister sites ;
- lister emails si script disponible ;
- détecter changements ;
- produire rapport.

## Actions interdites sans validation humaine

- créer email ;
- supprimer email ;
- changer mot de passe email ;
- modifier public_html ;
- supprimer fichier ;
- modifier .htaccess ;
- modifier wp-config.php ;
- modifier DNS ;
- modifier SSL ;
- redémarrer service critique ;
- nettoyer malware automatiquement.

## Mémoire projet

Écrire en mémoire uniquement :
- incidents confirmés ;
- procédures ops validées ;
- topologie durable ;
- décisions de sécurité validées.

Ne jamais écrire :
- mots de passe ;
- clés privées ;
- tokens ;
- secrets ;
- données personnelles inutiles.

## Rapport final

Format obligatoire :

RAPPORT_OPS_CPANEL:
SERVEUR:
SITES_ANALYSÉS:
EMAILS_ANALYSÉS:
SSL:
DISQUE:
FICHIERS_SUSPECTS:
FICHIERS_MODIFIÉS:
INCIDENTS:
ACTIONS_PROPOSÉES:
VALIDATION_HUMAINE_REQUISE:
