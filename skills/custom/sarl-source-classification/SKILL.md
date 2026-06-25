---
name: sarl-source-classification
description: Normaliser tout élément externe (email, agenda, drive, message social, Telegram) en un enregistrement structuré entreprise/projet avant triage ou dispatch. Utiliser par l'assistant personnel, le community-manager et tout agent qui ingère une source externe, pour décider owner, risque, sensibilité et agent assigné, et bloquer le dispatch quand le projet est inconnu.
---

# Classification des sources externes

Avant tout triage, dispatch ou action, chaque élément externe est normalisé en un
enregistrement unique. Objectif : router au bon agent, respecter la sensibilité et
forcer la validation humaine sur les actions sensibles.

## Schéma

```yaml
source_type: email | calendar | drive | linkedin | facebook | instagram | x | telegram
source_account: ""          # adresse / handle / compte d'origine
owner_type: personal | company | project
company_id: sarl-agent-ai | blockdevs | salon-du-cinema | onmovecinema | ong-yerda | unknown
project_id: ""              # vide si non rattaché à un projet précis
sensitivity: public | internal | confidential | secret
intent: question | task | incident | opportunity | community | support | admin
risk: low | medium | high | critical
actionability: info | draft | task | validation_required
assigned_agent: sarl-personal-assistant | community-manager | support-agent | ops-foundation
```

## Règles

- `project_id = unknown` ou `company_id = unknown` → **pas de dispatch automatique**,
  demander clarification.
- `sensitivity in {confidential, secret}` → ne jamais exposer le contenu dans les
  logs de l'orchestrateur ni dans un rapport ; résumer sans citer les données.
- `actionability = validation_required` → préparer un brouillon et escalader, ne
  jamais exécuter.
- `risk in {high, critical}` → validation humaine obligatoire avant toute action.
- Aucun secret (token, mot de passe, cookie) n'est stocké ni recopié.

## Mapping vers l'agent assigné

- email / calendar / drive personnels ou pro → `sarl-personal-assistant`.
- messages publics, commentaires, posts sociaux → `community-manager`.
- demande client / support → `support-agent`.
- incident système, serveur, cPanel → `ops-foundation`.

## Sortie pour une action sortante

Toute action externe proposée produit :

```text
ACTION_PROPOSEE:
COMPTE:
ENTREPRISE/PROJET:
RISQUE:
CONTENU:
VALIDATION_HUMAINE_REQUISE: oui
```
