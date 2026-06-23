# Profils experts et apprentissage autonome

## Objectif

Trois profils métier disposent d’une identité experte, d’un skill dédié, de
références officielles, de contrôles qualité et d’une veille autonome:

| Profil | Skill | Veille UTC |
|---|---|---|
| `designer-3d-agent` | `design-3d-production` | mardi 04:10 |
| `bureau-etudes-agent` | `engineering-design-office` | mercredi 04:20 |
| `community-manager` | `community-content-operations` | jeudi 04:30 |

## Modèle de connaissance

```text
SOUL.md
  définit rôle, responsabilité et limites
SKILL.md
  définit méthode de travail
references/
  contient workflows, contrôles et sources officielles
knowledge/CURRENT.md
  contient connaissances métier consolidées
knowledge/SOURCE_STATUS.md
  contient état courant des sources surveillées
knowledge/official-research/
  contient rapports datés et extraits indexés
knowledge/source-state.json
  contient empreintes SHA-256 pour détecter changements
```

## Apprentissage autonome

Le job `official-source-watch.py`:

1. lit manifest officiel du skill;
2. télécharge chaque source HTTPS avec limite de taille et timeout;
3. extrait titres, sections et paragraphes utiles;
4. calcule empreinte SHA-256;
5. compare à exécution précédente;
6. archive rapport daté;
7. met à jour `SOURCE_STATUS.md`;
8. livre résultat Telegram.

Mode `no-agent` évite boucles LLM, hallucinations, dépassement de contexte et
coût inutile. Agent expert utilise ensuite skill et snapshots pendant mission.

## Gouvernance

Agents peuvent:

- étudier sources officielles;
- conserver snapshots;
- détecter changements;
- expérimenter en sandbox;
- proposer évolution de méthode.

Agents ne peuvent pas automatiquement:

- modifier SOUL ou skill de référence;
- publier;
- certifier conformité;
- acheter;
- lancer action critique.

Ces actions exigent revue humaine. Cette séparation permet apprentissage
autonome sans dérive autonome.

## Workspace et activité

Recherche globale n’utilise plus SSE permanent. Elle appelle
`/api/activity-history`, snapshot JSON borné à 300 événements côté serveur et
200 événements côté recherche. Payload supérieur à 16 KiB et chunks de
streaming ne sont pas conservés.

Store Inspecteur conserve maximum 250 événements. Chat n’ouvre plus second
EventSource global: activité live arrive par flux actif de conversation.

## Installation reproductible

```bash
./scripts/install-expert-profiles.py
./scripts/install-maintenance-jobs.py
```

Puis:

```bash
docker cp scripts/configure-active-profiles.py \
  sarl-hermes-agent:/tmp/configure-active-profiles.py
docker exec sarl-hermes-agent \
  python /tmp/configure-active-profiles.py
```

## Validation

- Skills: `quick_validate.py`
- Veilles: statut cron `ok`, `last_error=None`, `last_delivery_error=None`
- Workspace: tests Vitest du ring buffer et store
- Plateforme: `./scripts/acceptance-test.sh`
