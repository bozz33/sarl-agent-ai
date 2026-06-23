# Etat de la stack Hermes

Date de l'audit : 18 juin 2026

Projet : SARL Agent AI

## Resume executif

La stack Hermes est installee sur un VPS Ubuntu Linux avec Docker Compose.
Hermes Agent et Hermes Workspace sont actifs et declares sains par Docker.

Etat principal :

- Hermes Agent : actif et sain.
- Hermes Workspace : actif et sain.
- Modele principal : `auto` via `openrouter`.
- Routage auxiliaire : Gemini, DeepSeek et Groq.
- PostgreSQL 16 : installe et actif.
- pgvector : non installe.
- Redis dans la stack Hermes : absent.
- Le Redis systeme du VPS est hors de la stack Hermes et reste intact.
- Projets Workspace : aucun projet present ou charge au demarrage.
- Acces actuel : local VPS uniquement, au moyen d'un tunnel SSH.
- Version declaree par le paquet Workspace : `2.2.0`.

## Reponses directes aux informations demandees

Cette section repond directement a chaque question. Les sections suivantes
fournissent les preuves et les explications techniques.

### 1. Mode d'installation actuel

| Question | Reponse directe |
|---|---|
| Docker Compose ? | Oui. C'est le mode d'installation principal de Hermes. |
| Installation manuelle ? | Non pour Hermes Agent et Hermes Workspace. Ils sont fournis par des images Docker. |
| systemd ? | Pas directement pour Hermes. `systemd` gere Docker. PostgreSQL et Redis sont des services systeme externes a Hermes. Les conteneurs Hermes utilisent `restart: unless-stopped`. |
| `pnpm dev` ? | Non. Aucun serveur de developpement `pnpm dev` n'est utilise. |
| VPS Linux uniquement ? | Oui. La stack est installee sur un VPS Ubuntu 24.04 LTS. Le PC Windows sert seulement a ouvrir un tunnel SSH et le navigateur. |

Fichier d'installation :

```text
/root/CascadeProjects/SARL-agent-ai/docker-compose.yml
```

### 2. Chemins reels

| Information | Chemin exact |
|---|---|
| Racine de la stack | `/root/CascadeProjects/SARL-agent-ai` |
| Hermes Workspace dans le conteneur | `/app` |
| Code source Workspace sur l'hote | Absent : Workspace provient de l'image Docker officielle |
| Runtime Workspace sur l'hote | `/root/CascadeProjects/SARL-agent-ai/workspace-runtime` |
| `~/.hermes` vu par Workspace | `/home/workspace/.hermes` |
| Repertoire Hermes vu par Agent | `/opt/data` |
| Volume Hermes sur l'hote | `/var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data` |
| Volume projets actuel dans Workspace | `/workspace` |
| Volume projets actuel sur l'hote | `/var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data` |
| Futur stockage recommande des projets | `/root/CascadeProjects/SARL-agent-ai/projects` |
| Skills Hermes actuels | `/home/workspace/.hermes/skills` dans Workspace, `/opt/data/skills` dans Agent |
| Futur stockage recommande des skills custom | `/root/CascadeProjects/SARL-agent-ai/skills/custom` |
| Skills Caveman de Codex, hors Hermes | `/root/CascadeProjects/SARL-agent-ai/.agents/skills` |

Les dossiers cibles `projects` et `skills/custom` sont les emplacements
recommandes pour la prochaine etape. Ils ne sont pas encore confirmes,
crees ou montes dans Compose.

### 3. Services deja actifs

| Question | Reponse directe |
|---|---|
| Gateway Hermes sur 8642 ? | Oui, actif et sain sur `127.0.0.1:8642` du VPS. |
| Dashboard API sur 9119 ? | Oui, actif sur `hermes-agent:9119` dans le reseau Docker. Il n'est pas publie sur l'hote. |
| Workspace sur 3000 ? | Oui, actif et sain sur `127.0.0.1:3000` du VPS. |
| PostgreSQL installe ? | Oui, PostgreSQL 16.14 est installe comme service systeme du VPS, hors Docker Hermes. |
| pgvector installe ? | Non. |
| Redis installe dans Hermes ? | Non. Aucun conteneur, port, volume ou parametre Redis dans la stack Hermes. |
| Redis installe sur le VPS ? | Oui, comme service systeme externe. Il reste intact pour ne pas affecter WordPress. |

Services Docker de la stack Hermes :

```text
hermes-agent
hermes-workspace
```

### 4. Modeles reellement visibles dans le Dashboard

La liste principale renvoyee par `/api/models` contient uniquement :

```text
auto            fournisseur openrouter
hermes-agent    modele virtuel du gateway
```

Reponse detaillee pour chaque famille demandee :

| Famille demandee | Nom exact trouve | Visible dans la liste principale ? | Etat reel |
|---|---|---|---|
| Gemini | `gemini-2.5-flash` | Non | Configure pour vision, extraction web et curator |
| Gemini Swarm | `gemini/gemini-2.5-flash` | Non | Declare pour le profil Researcher |
| DeepSeek | `deepseek-chat` | Non | Configure pour Skills Hub |
| DeepSeek | `deepseek-reasoner` | Non | Configure pour triage et Kanban |
| DeepSeek Swarm | `deepseek/deepseek-chat` | Non | Declare pour Builder |
| DeepSeek Swarm | `deepseek/deepseek-reasoner` | Non | Declare pour Reviewer |
| Groq | `llama-3.1-8b-instant` | Non | Configure pour compression et taches rapides |
| Groq Swarm | `groq/llama-3.1-8b-instant` | Non | Declare pour Ops |
| Groq Swarm | `groq/qwen/qwen3-32b` | Non | Declare pour QA |
| OpenRouter | `auto` | Oui | Modele principal actif |
| OpenRouter Swarm | `openrouter/poolside/laguna-m.1:free` | Non | Declare pour Orchestrator |
| Claude | Aucun nom de modele | Non | Identifiants absents, `missing_credentials` |
| Codex | Aucun nom de modele | Non | Carte fournisseur presente, mais identifiants absents et aucun modele expose |

Conclusion :

- OpenRouter `auto` est le seul modele principal reellement selectionne.
- Gemini, DeepSeek et Groq sont configures dans les fonctions auxiliaires ou
  declares dans `swarm.yaml`.
- Une declaration Swarm ne prouve pas qu'un worker persistant est lance.
- Claude et Codex ne sont pas encore operationnels dans Hermes.

### 5. Niveau de securite souhaite

La seule decision deja appliquee est l'acces local par tunnel SSH pour un seul
administrateur. Tailscale est la recommandation cible, mais reste a confirmer
et a installer.

| Question | Etat ou recommandation |
|---|---|
| Acces local seulement ? | Oui pour les ports applicatifs : ils restent lies a `127.0.0.1`. |
| Acces via domaine ? | Non pour le moment. |
| Acces via Tailscale ? | Recommande pour un acces prive et stable. Pas encore confirme ni installe. |
| Acces public avec reverse proxy ? | Non. Aucun port Hermes ne doit etre publie directement sur Internet. |
| Plusieurs utilisateurs ou toi seul ? | Un seul administrateur pour la premiere version. |
| Acces actuel | Tunnel SSH depuis le PC Windows. |
| Acces de secours futur | Tunnel SSH conserve apres ajout de Tailscale. |

Architecture de securite recommandee :

```text
Administrateur unique
  -> Tailscale prive
  -> Hermes Workspace sur port local 3000
  -> Hermes Agent et Dashboard sur reseau prive
```

### 6. Projets reels au demarrage

Decision globale :

```text
PAS DE PROJET AU DEMARRAGE
```

| Projet demande | Charge au demarrage de Hermes ? | Etat |
|---|---|---|
| BlockDevs | Non | Absent du volume `/workspace` |
| Salon du Cinema | Non | Le site existe comme stack WordPress separee, mais n'est pas un projet charge par Hermes |
| OnMoveCinema | Non | Absent du volume `/workspace` |
| ONG Yerda | Non | Absent du volume `/workspace` |
| Autres projets | Non | Aucun projet present dans `/workspace` |

Le dossier `flowguard` existe ailleurs sur le VPS, mais il n'est pas monte dans
Hermes Workspace et ne demarre pas avec Hermes.

Le volume `/workspace` est vide. Les six profils de `swarm.yaml` sont des
declarations de roles et non des projets automatiquement charges.

### 7. Memoire projet

| Question | Reponse directe |
|---|---|
| PostgreSQL disponible ? | Oui, PostgreSQL 16.14 est actif sur `127.0.0.1:5432`. |
| pgvector disponible ? | Non, l'extension n'est pas installee. |
| Base de donnees memoire projet creee ? | Non. Seule la base systeme `postgres` existe actuellement. |
| MCP memoire en Node.js ou Python ? | Aucune preference utilisateur explicite n'a encore ete donnee. Python est recommande. |
| Stocker aussi les fichiers sources et documents ? | Recommande : oui, dans une arborescence projet persistante. Decision finale a confirmer. |
| Stocker les gros fichiers dans PostgreSQL ? | Non. PostgreSQL conserve les metadonnees, embeddings, chemins et empreintes. |

Arborescence cible :

```text
/root/CascadeProjects/SARL-agent-ai/projects/
└── <project-id>/
    ├── source/
    ├── documents/
    ├── generated/
    ├── reports/
    ├── artifacts/
    └── project.yaml
```

## 1. Mode d'installation actuel

| Element | Etat |
|---|---|
| Docker Compose | Oui, methode principale |
| Installation manuelle | Non pour les applications Hermes |
| systemd | Docker et PostgreSQL utilisent des services systeme |
| `pnpm dev` | Non |
| VPS Linux | Oui, Ubuntu 24.04 LTS |
| Environnement de production | Conteneurs Docker avec `restart: unless-stopped` |

Le fichier d'orchestration est :

```text
/root/CascadeProjects/SARL-agent-ai/docker-compose.yml
```

Services Docker Compose :

```text
hermes-agent
hermes-workspace
```

Hermes Workspace est execute depuis l'image :

```text
ghcr.io/outsourc-e/hermes-workspace:latest
```

Il ne s'agit pas d'un serveur de developpement `pnpm dev`.

## 2. Chemins reels

### Racine du projet sur le VPS

```text
/root/CascadeProjects/SARL-agent-ai
```

### Hermes Workspace

Il n'existe pas actuellement de copie du code source Workspace sur l'hote.
Workspace est fourni par une image Docker.

```text
Dans le conteneur : /app
Configuration Compose : /root/CascadeProjects/SARL-agent-ai/docker-compose.yml
Runtime persistant : /root/CascadeProjects/SARL-agent-ai/workspace-runtime
```

### Repertoire Hermes

Hermes Agent et Workspace partagent le meme volume Docker :

```text
Agent : /opt/data
Workspace : /home/workspace/.hermes
Hote : /var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data
```

Le fichier de configuration reel est :

```text
/opt/data/config.yaml
```

Le fichier de secrets reel dans le conteneur Agent est :

```text
/opt/data/.env
```

Les secrets sources du projet restent dans :

```text
/root/CascadeProjects/SARL-agent-ai/.secrets
```

### Stockage des projets

Etat actuel :

```text
Workspace : /workspace
Volume Docker : sarl-agent-ai_hermes-workspace-files
Hote : /var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data
```

Ce volume est actuellement vide.

Chemin hote recommande pour la prochaine architecture :

```text
/root/CascadeProjects/SARL-agent-ai/projects
```

Ce dossier devra etre monte dans Workspace sur :

```text
/workspace
```

Un montage bind explicite est preferable a un volume Docker opaque pour les
sauvegardes, les inspections et les migrations.

### Skills

Skills Hermes fournis et geres par Hermes :

```text
Agent : /opt/data/skills
Workspace : /home/workspace/.hermes/skills
Hote : /var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data/skills
```

Chemin recommande pour les futurs skills personnalises :

```text
/root/CascadeProjects/SARL-agent-ai/skills/custom
```

Ce dossier pourra etre monte dans le conteneur et declare dans :

```yaml
skills:
  external_dirs:
    - /opt/custom-skills
```

Le dossier suivant contient Caveman pour Codex et ne doit pas etre confondu
avec les skills Hermes :

```text
/root/CascadeProjects/SARL-agent-ai/.agents/skills
```

## 3. Services deja actifs

| Service | Etat | Exposition |
|---|---|---|
| Hermes Gateway | Actif et sain | `127.0.0.1:8642` sur le VPS |
| Hermes Dashboard API | Actif | `hermes-agent:9119`, reseau Docker uniquement |
| Hermes Workspace | Actif et sain | `127.0.0.1:3000` sur le VPS |
| PostgreSQL | Actif, version 16.14 | `127.0.0.1:5432` |
| pgvector | Non installe | A installer |
| Redis dans Hermes | Absent | Aucun conteneur, port ou parametre Redis |

Le port Dashboard `9119` n'est pas publie directement sur l'hote. Workspace
y accede par le reseau Docker :

```text
http://hermes-agent:9119
```

La stack Docker Hermes ne contient aucun service Redis :

```text
hermes-agent
hermes-workspace
```

Il n'existe dans sa configuration aucun conteneur Redis, aucune variable Redis
et aucun port `6379`. Il n'y avait donc rien a supprimer dans la stack Hermes.

Un service Redis existe separement sur le VPS. Il est hors de cette stack et
n'a pas ete arrete ou desinstalle, afin de ne pas affecter WordPress ou un
autre service du serveur.

PostgreSQL ne contient actuellement que la base systeme `postgres`.
Aucune base de memoire projet n'a encore ete creee.

## 4. Modeles et fournisseurs reellement visibles

### Modeles exposes dans la liste principale du Dashboard

L'API Workspace `/api/models` retourne actuellement seulement :

| Identifiant | Fournisseur | Role |
|---|---|---|
| `auto` | `openrouter` | Modele principal actif |
| `hermes-agent` | `hermes` | Modele virtuel representant le gateway |

Cela signifie que tous les modeles utilises par le routage ne sont pas
necessairement affiches dans la liste principale.

### Modeles configures dans Hermes et Swarm

| Famille | Identifiants exacts trouves | Usage actuel |
|---|---|---|
| Gemini | `gemini-2.5-flash` | Vision, extraction web, curator |
| Gemini Swarm | `gemini/gemini-2.5-flash` | Agent Researcher |
| DeepSeek | `deepseek-chat` | Skills Hub |
| DeepSeek | `deepseek-reasoner` | Triage et decomposition Kanban |
| DeepSeek Swarm | `deepseek/deepseek-chat` | Agent Builder |
| DeepSeek Swarm | `deepseek/deepseek-reasoner` | Agent Reviewer |
| Groq | `llama-3.1-8b-instant` | Compression et taches rapides |
| Groq Swarm | `groq/llama-3.1-8b-instant` | Agent Ops |
| Groq Swarm | `groq/qwen/qwen3-32b` | Agent QA |
| OpenRouter | `auto` | Modele principal actif |
| OpenRouter Swarm | `openrouter/poolside/laguna-m.1:free` | Orchestrateur |
| Claude | Aucun modele | Non configure dans Hermes |
| Codex | Aucun modele exact expose | Fournisseur affiche, mais authentification non operationnelle |

### Cles presentes

Les variables suivantes sont presentes dans Hermes Agent :

```text
OPENROUTER_API_KEY
GEMINI_API_KEY
GOOGLE_API_KEY
DEEPSEEK_API_KEY
GROQ_API_KEY
```

Les valeurs ne sont volontairement pas reproduites dans ce document.

### Claude et Codex

Le diagnostic d'usage Workspace indique :

```text
Claude OAuth : missing_credentials
Codex : missing_credentials
OpenAI API : missing_credentials
```

Le Dashboard peut afficher la carte `OpenAI Codex` comme configuree, mais
aucun modele Codex n'est expose et le diagnostic ne trouve pas ses
identifiants dans l'environnement Workspace/Hermes.

Conclusion :

- Claude n'est pas active.
- Codex n'est pas encore utilisable par Hermes.
- Les authentifications presentes sur l'hote ne sont pas encore integrees
  au volume partage Hermes.

### Routage intelligent

Le routage intelligent est active :

```yaml
smart_model_routing:
  enabled: true
  cheap_model: groq/llama-3.1-8b-instant
  max_simple_chars: 600
  max_simple_words: 80
```

Le fournisseur principal est :

```yaml
model:
  provider: openrouter
  default: auto
```

Points d'attention :

- `fallback_providers` est actuellement vide. Le routage auxiliaire existe,
  mais aucune chaine globale de fournisseurs de secours n'est encore definie.
- Un ancien champ racine `provider: nous` subsiste dans `config.yaml`.
  Le bloc moderne `model.provider: openrouter` est celui utilise par Workspace,
  mais ce champ historique doit etre supprime lors d'une prochaine
  normalisation de la configuration.
- La cle OpenRouter est disponible dans Hermes Agent. Le diagnostic local
  `provider-usage` de Workspace ne la voit toutefois pas directement, car le
  fichier `providers.env` est injecte dans le conteneur Agent et non dans le
  conteneur Workspace. Workspace accede au fournisseur par l'API Hermes.

## 5. Niveau de securite

### Etat actuel

| Option | Etat |
|---|---|
| Acces local uniquement | Oui |
| Tunnel SSH | Oui |
| Domaine public | Non |
| Tailscale | Non configure |
| Reverse proxy public | Non |
| Utilisateurs | Un seul administrateur |
| Protection Workspace | Mot de passe |

Les ports `3000` et `8642` sont lies a `127.0.0.1`. Ils ne sont donc pas
directement accessibles depuis Internet.

### Architecture recommandee

Pour le besoin actuel :

```text
Utilisateur unique
  -> Tailscale prive
  -> Hermes Workspace
  -> Hermes Agent
```

Recommandation :

1. Conserver les ports Hermes lies a `127.0.0.1`.
2. Ajouter Tailscale pour un acces prive stable.
3. Conserver SSH comme acces de secours.
4. Ne pas publier directement les ports `3000`, `8642` ou `9119`.
5. Ne mettre en place un domaine et un reverse proxy HTTPS que si plusieurs
   utilisateurs externes doivent acceder a Workspace.

## 6. Projets au demarrage

Decision :

```text
PAS DE PROJET AU DEMARRAGE
```

Le volume `/workspace` est actuellement vide.

Comportement cible :

- Workspace demarre sans ouvrir de projet.
- Aucun agent Swarm n'est lance automatiquement sur un projet.
- Aucun depot n'est clone automatiquement.
- Aucun projet n'est monte par defaut.
- Un projet est cree ou selectionne explicitement depuis Workspace.

Les six profils presents dans `swarm.yaml` sont des declarations de workers.
Ils ne correspondent pas encore a six processus persistants actuellement
demarres. Aucun worker de projet ne doit etre lance automatiquement.

Le futur dossier hote pourra etre :

```text
/root/CascadeProjects/SARL-agent-ai/projects
```

## 7. Memoire projet

### Etat actuel

| Composant | Etat |
|---|---|
| PostgreSQL 16 | Disponible et actif |
| pgvector | Non installe |
| Base de donnees projet | Non creee |
| MCP memoire projet | Non implemente |
| Memoire interne Hermes | Active |
| Fichiers projet dans `/workspace` | Aucun actuellement |

La memoire interne Hermes existe deja, mais elle ne remplace pas la future
memoire structuree par projet dans PostgreSQL.

### Choix recommande pour le MCP memoire

Langage recommande :

```text
Python
```

Raisons :

- Hermes Agent est principalement en Python.
- Bibliotheques PostgreSQL et pgvector matures.
- Integration simple avec `psycopg`, `pgvector` et un serveur MCP Python.
- Meilleure reutilisation future pour le traitement de documents, les
  embeddings et les pipelines d'indexation.

Node.js reste possible, mais n'apporte pas d'avantage decisif pour ce service
de memoire.

### Stockage des fichiers et documents

Oui, les fichiers sources et documents doivent etre conserves dans une
arborescence projet en plus des vecteurs PostgreSQL.

Structure recommandee :

```text
/root/CascadeProjects/SARL-agent-ai/projects/
└── <project-id>/
    ├── source/
    ├── documents/
    ├── generated/
    ├── reports/
    ├── artifacts/
    └── project.yaml
```

PostgreSQL/pgvector doit contenir :

- identifiants des projets ;
- metadonnees ;
- fragments de documents ;
- embeddings ;
- liens vers les fichiers ;
- historique des decisions ;
- rapports et handoffs des agents.

Les fichiers volumineux ne doivent pas etre stockes directement dans la base.
La base doit conserver leur chemin, leur empreinte et leurs metadonnees.

## Architecture cible retenue

```text
Tailscale ou tunnel SSH
        |
Hermes Workspace :3000
        |
Hermes Agent :8642
        |
        +-- Dashboard API :9119
        +-- OpenRouter / auto
        +-- Gemini
        +-- DeepSeek
        +-- Groq
        +-- Swarm
        |
MCP Project Memory en Python
        |
PostgreSQL 16 + pgvector
        |
/root/CascadeProjects/SARL-agent-ai/projects
```

## Actions restantes

1. Installer l'extension PostgreSQL `pgvector`.
2. Creer une base et un utilisateur dedies a la memoire projet.
3. Creer le MCP Project Memory en Python.
4. Remplacer le volume opaque `/workspace` par un montage du dossier
   `/root/CascadeProjects/SARL-agent-ai/projects`.
5. Creer le dossier versionne des skills personnalises.
6. Integrer correctement les authentifications Claude et Codex dans Hermes.
7. Ajouter Tailscale pour supprimer la dependance au proxy temporaire Codex.
8. Tester chaque modele avec une requete reelle avant de le declarer actif.
