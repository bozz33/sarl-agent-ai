# SARL-Agent-AI — Document complet de mise en place Hermes Agent / Hermes Workspace

**Version : 1.3**  
**Date : 18 juin 2026**  
**Auteur projet : Alain Francis**  
**Objet :** architecture enterprise multi-projets, multi-agents, mémoire projet, orchestration avancée, modèles coût/qualité, sandbox, gouvernance, communication inter-agents et maintenance supervisée de la stack Hermes.

---

## 0. Résumé exécutif

Le but de SARL-Agent-AI est de transformer Hermes Workspace en poste de pilotage d’une équipe numérique interne composée d’agents spécialisés capables de travailler sur plusieurs projets, de collaborer, de produire des livrables, de conserver une mémoire projet, de limiter les coûts modèles et d’évoluer sous supervision humaine.

La stack actuelle est saine et opérationnelle : Hermes Agent et Hermes Workspace tournent en Docker Compose sur un VPS Ubuntu, avec accès local via tunnel SSH. PostgreSQL 16 est actif hors Docker, mais pgvector n’est pas encore installé. OpenRouter, Gemini, DeepSeek et Groq sont disponibles. Claude et Codex sont prévus dans l’architecture cible, mais doivent encore être activés correctement dans Hermes.

Le principe d’architecture retenu est :

```text
Hermes Workspace        = cockpit / poste de pilotage
Profiles Hermes         = agents permanents réels
Swarm                   = coordination live des agents
Kanban                  = tâches durables, handoffs, échanges inter-agents
delegate_task           = sous-agents temporaires pour sous-tâches courtes
AGENTS.md / .hermes.md  = contexte projet
SOUL.md                 = identité et règles du profil/agent
Skills                  = procédures réutilisables
MCP                     = accès aux outils externes
PostgreSQL + pgvector   = mémoire métier projet isolée par project_id
Docker sandbox          = bac à sable d’exécution
Git worktrees           = isolation des travaux code par agent
Checkpoints             = rollback avant modification
Hooks                   = garde-fous techniques
sarl-governor           = contrôle de conformité
sarl-stack-steward      = évolution supervisée de la stack
```

La règle centrale :

```text
Les agents peuvent analyser, proposer, tester, documenter et préparer.
Ils ne doivent pas exécuter d’action critique sans validation humaine.
```

---

## 1. Décisions d’architecture retenues

### 1.1 Décisions principales

| Sujet | Décision retenue |
|---|---|
| Accès à Workspace | Tailscale comme cible privée, tunnel SSH conservé en secours |
| Exposition publique | Aucun port Hermes publié directement sur Internet |
| Dossier officiel des projets | `/root/CascadeProjects/SARL-agent-ai/projects` |
| Dossier officiel des skills custom | `/root/CascadeProjects/SARL-agent-ai/skills/custom` |
| MCP mémoire projet | Python |
| Mémoire projet | PostgreSQL 16 + pgvector via MCP custom |
| Mémoire native Hermes | Conservée pour la mémoire propre à chaque profil |
| Orchestration | Router économique + orchestrateur normal + orchestrateur critique |
| Premium models | Claude/GPT/Codex réservés aux tâches critiques ou avancées |
| Bacs à sable | Docker backend + worktrees + checkpoints |
| Communication agents | Kanban + Swarm + rapports + mémoire projet + delegate_task |
| Maintenance évolutive | `sarl-stack-steward` supervisé par `sarl-governor` et humain |

### 1.2 Décisions de prudence

- Ne pas modifier directement le profil Hermes principal existant.
- Créer les nouveaux agents sous forme de profiles clonés ou dédiés.
- Ne pas démarrer tous les workers Swarm automatiquement au boot.
- Ne pas charger de projet au démarrage.
- Ne pas utiliser PostgreSQL/pgvector comme mémoire native Hermes, mais comme mémoire métier externe exposée via MCP.
- Ne pas considérer le fallback provider comme une escalade intelligente : le fallback sert aux pannes/quota, l’escalade sert au risque/complexité.
- Ne pas considérer un profile comme un sandbox : le profile isole l’état agent, le sandbox isole l’exécution.

---

## 2. État réel de la stack actuelle

### 2.1 Installation

```text
OS VPS                         : Ubuntu 24.04 LTS
Mode installation Hermes        : Docker Compose
Services Docker                 : hermes-agent, hermes-workspace
Workspace image                 : ghcr.io/outsourc-e/hermes-workspace:latest
Workspace version déclarée      : 2.2.0
pnpm dev                        : non utilisé
systemd                         : gère Docker, PostgreSQL et Redis système
Accès actuel                    : tunnel SSH depuis Windows
```

### 2.2 Chemins réels

```text
Racine stack hôte :
/root/CascadeProjects/SARL-agent-ai

Docker Compose :
/root/CascadeProjects/SARL-agent-ai/docker-compose.yml

Runtime Workspace hôte :
/root/CascadeProjects/SARL-agent-ai/workspace-runtime

Hermes Agent dans conteneur :
/opt/data

Hermes Workspace dans conteneur :
/home/workspace/.hermes

Volume Hermes hôte :
/var/lib/docker/volumes/sarl-agent-ai_hermes-agent-data/_data

Workspace fichiers actuel dans conteneur :
/workspace

Volume Workspace actuel hôte :
/var/lib/docker/volumes/sarl-agent-ai_hermes-workspace-files/_data

Dossier officiel cible des projets :
/root/CascadeProjects/SARL-agent-ai/projects

Dossier officiel cible des skills custom :
/root/CascadeProjects/SARL-agent-ai/skills/custom

Secrets sources :
/root/CascadeProjects/SARL-agent-ai/.secrets

Skills Caveman/Codex hors Hermes :
/root/CascadeProjects/SARL-agent-ai/.agents/skills
```

### 2.3 Services actifs

```text
Hermes Gateway      : actif, 127.0.0.1:8642
Hermes Dashboard API: actif dans réseau Docker, hermes-agent:9119
Hermes Workspace    : actif, 127.0.0.1:3000
PostgreSQL          : actif, 127.0.0.1:5432, version 16.14
pgvector            : non installé
Redis dans Hermes   : absent
Redis système VPS   : présent hors stack Hermes, à ne pas toucher
```

### 2.4 Modèles et providers

Actuel :

```text
OpenRouter:
  auto
  -> modèle principal actif

Gemini:
  gemini-2.5-flash
  -> vision, extraction web, curator, recherche

DeepSeek:
  deepseek-chat
  deepseek-reasoner
  -> skills hub, triage, Kanban, builder/reviewer

Groq:
  llama-3.1-8b-instant
  qwen/qwen3-32b
  -> compression, tâches rapides, QA/Ops

Claude:
  missing_credentials actuellement
  -> prévu pour critique

Codex / OpenAI:
  missing_credentials actuellement
  -> prévu pour code avancé et tâches critiques
```

### 2.5 Projets au démarrage

Décision actuelle correcte :

```text
Aucun projet chargé au démarrage.
Aucun worker projet lancé automatiquement.
Aucun dépôt cloné automatiquement.
Workspace démarre vide.
L’administrateur choisit explicitement le projet.
```

---

## 3. Ce qui vient de la documentation officielle, ce qui est personnalisé

### 3.1 Confirmé officiellement

Les briques suivantes sont documentées par Hermes Agent / Hermes Workspace :

- profiles Hermes ;
- configuration `config.yaml` et `.env` ;
- modèles principaux et auxiliaires ;
- context files : `.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `SOUL.md` ;
- skills ;
- MCP ;
- web dashboard ;
- fallback providers ;
- cron jobs ;
- Kanban ;
- delegation / `delegate_task` ;
- Docker backend / sandbox ;
- Docker install ;
- Git worktrees ;
- checkpoints et rollback ;
- hooks ;
- Workspace Swarm, Operations, Conductor.

### 3.2 Déduit proprement

Ces éléments sont des choix cohérents avec la documentation :

- un profile Hermes par agent spécialisé ;
- un board Kanban par projet ;
- un `AGENTS.md` par projet ;
- un MCP custom pour exposer une mémoire métier ;
- un router économique séparé de l’orchestrateur normal ;
- un orchestrateur critique séparé pour Claude/GPT/Codex ;
- un agent de gouvernance ;
- un agent de maintenance supervisée.

### 3.3 Personnalisé SARL-Agent-AI

Ces éléments sont propres à ton architecture :

- `sarl-router` ;
- `sarl-orchestrator` ;
- `sarl-orchestrator-critical` ;
- `sarl-governor` ;
- `sarl-stack-steward` ;
- mémoire projet PostgreSQL/pgvector ;
- schéma des tables mémoire ;
- politique coût/risque ;
- règles métier SARL ;
- structure `/root/CascadeProjects/SARL-agent-ai/projects`.

### 3.4 Point de vigilance

PostgreSQL/pgvector n’est pas traité ici comme un provider mémoire natif Hermes. C’est une mémoire métier externe, exposée via un serveur MCP personnalisé.

---

## 4. Architecture cible globale

```text
Administrateur
  |
  | SSH tunnel ou Tailscale
  v
Hermes Workspace :3000
  |
  +-- Chat / Files / Terminal / Operations / Conductor / Swarm
  |
  v
Hermes Gateway :8642
  |
  +-- Profiles Hermes
  |     +-- sarl-router
  |     +-- sarl-orchestrator
  |     +-- sarl-orchestrator-critical
  |     +-- sarl-governor
  |     +-- sarl-stack-steward
  |     +-- code-builder
  |     +-- codex-builder
  |     +-- code-reviewer
  |     +-- code-reviewer-critical
  |     +-- research-sage
  |     +-- docs-scribe
  |     +-- qa-agent
  |     +-- ops-foundation
  |     +-- community-manager
  |     +-- support-agent
  |     +-- bureau-etudes-agent
  |     +-- designer-3d-agent
  |
  +-- Kanban boards
  |     +-- sarl-agent-ai
  |     +-- blockdevs
  |     +-- salon-cinema
  |     +-- onmovecinema
  |     +-- ong-yerda
  |
  +-- MCP servers
  |     +-- sarl-project-memory-mcp
  |     +-- filesystem project MCP
  |     +-- GitHub MCP
  |     +-- future APIs métier
  |
  v
PostgreSQL 16 + pgvector
  |
  +-- project memory
  +-- semantic chunks
  +-- decisions
  +-- handoffs
  +-- reports
  +-- agent activity logs
  |
  v
/root/CascadeProjects/SARL-agent-ai/projects
  |
  +-- blockdevs
  +-- salon-cinema
  +-- onmovecinema
  +-- ong-yerda
```

---

## 5. Cœur technique : Profile ou Swarm ?

La réponse retenue :

```text
Le cœur technique de l’agent = Profile.
Le cœur collaboratif = Swarm.
Le cœur durable du travail = Kanban.
Le cœur mémoire projet = PostgreSQL/pgvector via MCP.
```

Un profile Hermes représente un agent permanent avec sa propre identité, sa configuration, son modèle, ses skills, sa mémoire native et ses sessions.

Swarm ne remplace pas les profiles : il orchestre des profiles.

Kanban ne remplace pas Swarm : il assure la persistance des tâches, commentaires, validations et handoffs.

---

## 6. Agents permanents et responsabilités

### 6.1 Couche de direction

| Profile | Rôle | Modèles |
|---|---|---|
| `sarl-router` | Triage économique, classification projet/niveau/agent | Groq / Gemini Flash |
| `sarl-orchestrator` | Orchestration quotidienne, découpage, suivi | Gemini / DeepSeek / OpenRouter fiable |
| `sarl-orchestrator-critical` | Décisions critiques, arbitrage, validation risques | Claude / GPT avancé |
| `sarl-governor` | Audit des règles, escalades, coûts, validations | économique, premium si audit critique |
| `sarl-stack-steward` | Maintenance supervisée de la stack Hermes | économique + recherche officielle |

### 6.2 Couche développement

| Profile | Rôle | Modèles |
|---|---|---|
| `code-builder` | Développement courant, corrections, refactor simple | DeepSeek / OpenRouter |
| `codex-builder` | Développement avancé, gros refactor, code complexe | Codex / OpenAI / GPT selon activation |
| `code-reviewer` | Revue standard | DeepSeek Reasoner |
| `code-reviewer-critical` | Revue sécurité/production/architecture | Claude / GPT |
| `qa-agent` | Tests, reproduction bugs, validation | Groq qwen / DeepSeek |

### 6.3 Couche métier

| Profile | Rôle | Modèles |
|---|---|---|
| `research-sage` | Veille, benchmark, recherche | Gemini 2.5 Flash / DeepSeek |
| `docs-scribe` | Documentation, rapports, synthèses | Gemini / Groq |
| `community-manager` | Contenu réseaux sociaux, calendrier éditorial | Gemini / Groq |
| `support-agent` | Support client, triage tickets | Gemini / Groq |
| `bureau-etudes-agent` | Études techniques, notes de calcul | DeepSeek / premium selon criticité |
| `designer-3d-agent` | Visualisation 3D, Blender, rendu | Gemini vision / outils 3D / premium selon besoin |
| `ops-foundation` | Supervision VPS, services, logs | Groq / Gemini, actions critiques bloquées |

---

## 7. Orchestration avancée

### 7.1 Flux général

```text
Demande utilisateur
  |
  v
sarl-router
  - détecte le projet
  - classe la criticité
  - choisit l’agent cible
  |
  v
sarl-orchestrator
  - consulte AGENTS.md
  - consulte mémoire projet
  - découpe en tâches
  - crée tâches Kanban
  - supervise agents
  |
  +--> tâche simple
  |      -> docs-scribe / research-sage / community-manager
  |
  +--> tâche standard
  |      -> agent spécialisé économique
  |
  +--> tâche avancée
  |      -> code-builder / qa-agent / reviewer
  |
  +--> tâche critique
         -> sarl-orchestrator-critical
         -> code-reviewer-critical si code
         -> validation humaine obligatoire
```

### 7.2 Classification des tâches

| Niveau | Description | Modèles | Validation |
|---|---|---|---|
| SIMPLE | résumé, reformulation, extraction simple | Groq / Gemini Flash | non |
| STANDARD | contenu, veille, documentation, support simple | Gemini / DeepSeek / Groq | selon publication |
| AVANCÉE | développement, debug, architecture simple, intégration | DeepSeek / Codex / reviewer | parfois |
| CRITIQUE | production, sécurité, DB, paiement, données, contrat, juridique | Claude/GPT/Codex avancé | oui obligatoire |

### 7.3 Critères de criticité

Une tâche devient critique si elle touche au moins un de ces éléments :

```text
production
déploiement
migration
base de données
suppression de données
sécurité
secrets, tokens, clés API
paiement
contrat
juridique
données personnelles / RGPD
VPS / DNS / reverse proxy
publication officielle
décision client importante
action irréversible
coût financier significatif
```

### 7.4 Règle d’incertitude

```text
Si l’orchestrateur hésite entre AVANCÉE et CRITIQUE,
il classe temporairement CRITIQUE et escalade.
```

### 7.5 Escalade concrète

L’escalade se fait par Kanban :

```text
sarl-orchestrator
  -> crée une tâche Kanban
  -> assigne à sarl-orchestrator-critical
  -> joint contexte, risques, mémoire, options
  -> attend avis
  -> demande validation humaine si nécessaire
```

Format du dossier d’escalade :

```markdown
# Escalade critique

## Projet
<project_id>

## Demande initiale
...

## Pourquoi c’est critique
...

## Contexte projet
...

## Mémoire pertinente
...

## Options possibles
1. ...
2. ...
3. ...

## Risques
...

## Décision attendue
...

## Validation humaine requise
Oui / Non
```

---

## 8. Stratégie modèles

### 8.1 Principe

```text
Toujours utiliser le modèle le moins coûteux capable de réussir correctement la tâche.
Ne jamais utiliser un modèle gratuit peu fiable pour une décision critique.
Ne jamais utiliser Claude/GPT/Codex en permanence.
```

### 8.2 Matrice cible

| Usage | Premier choix | Fallback technique | Escalade intelligente |
|---|---|---|---|
| Triage court | Groq / Gemini Flash | OpenRouter free fiable | sarl-orchestrator |
| Résumé simple | Gemini Flash | Groq | aucun |
| Documentation | Gemini / Groq | OpenRouter | reviewer si livrable client |
| Recherche | Gemini / DeepSeek | OpenRouter | research-sage premium ponctuel |
| Développement courant | DeepSeek | OpenRouter | codex-builder |
| Debug complexe | DeepSeek Reasoner | Codex | code-reviewer-critical |
| Architecture | DeepSeek Reasoner | Claude/GPT | orchestrator-critical |
| Revue sécurité | Claude/GPT | autre premium | validation humaine |
| Production / DB | Claude/GPT + humain | aucun automatique | validation obligatoire |
| Code avancé | Codex | GPT/Claude selon tâche | review critical |

### 8.3 Actuel vs cible

Actuel :

```text
OpenRouter auto = principal actif.
Gemini / DeepSeek / Groq = disponibles pour auxiliaire et Swarm.
Claude / Codex = non opérationnels, credentials manquants.
```

Cible :

```text
Claude = critique, architecture, revue, sécurité.
Codex = code avancé, gros refactor, édition complexe, debug.
OpenRouter = fallback et routage économique.
Gemini/Groq/DeepSeek = quotidien économique.
```

### 8.4 Fallback providers

Le fallback technique sert quand un provider échoue :

```text
- erreur API ;
- rate limit ;
- quota ;
- indisponibilité ;
- problème réseau.
```

Il ne sert pas à déterminer si une tâche est critique.

La configuration finale doit ajouter une chaîne `fallback_providers`, actuellement vide.

Exemple conceptuel :

```yaml
fallback_providers:
  - provider: openrouter
    model: auto
  - provider: gemini
    model: gemini-2.5-flash
  - provider: deepseek
    model: deepseek-chat
```

À adapter aux noms exacts validés dans le Dashboard Hermes au moment de l’implémentation.

---

## 9. Contextes projet

### 9.1 Fichier de contexte principal

Chaque projet doit contenir :

```text
AGENTS.md
```

Le contexte projet ne doit pas être uniquement dans une conversation ou dans la mémoire. Il doit vivre avec le projet.

### 9.2 Structure projet officielle

```text
/root/CascadeProjects/SARL-agent-ai/projects/
├── blockdevs/
│   ├── AGENTS.md
│   ├── README.md
│   ├── project.yaml
│   ├── source/
│   ├── documents/
│   ├── generated/
│   ├── reports/
│   ├── artifacts/
│   ├── worktrees/
│   └── memory/
├── salon-cinema/
├── onmovecinema/
└── ong-yerda/
```

### 9.3 Template `project.yaml`

```yaml
project_id: blockdevs
name: BlockDevs
status: active
owner: Alain Francis
visibility: internal

workspace:
  root: /workspace/blockdevs
  host_root: /root/CascadeProjects/SARL-agent-ai/projects/blockdevs

memory:
  backend: sarl-project-memory-mcp
  project_id: blockdevs
  write_policy: validated_or_tagged
  truth_status_required: true

kanban:
  board: blockdevs

agents:
  default_orchestrator: sarl-orchestrator
  builder: code-builder
  reviewer: code-reviewer
  qa: qa-agent
  scribe: docs-scribe
  research: research-sage

human_validation_required_for:
  - production
  - deployment
  - database_migration
  - data_deletion
  - public_publication
  - secrets
  - client_final_delivery
```

### 9.4 Template `AGENTS.md`

```markdown
# Projet : BlockDevs

## Identité

Project ID : blockdevs  
Nom : BlockDevs  
Responsable : Alain Francis  
Type : développement logiciel / automatisation

## Objectif

Ce projet contient les travaux liés à BlockDevs.

## Dossiers

- `source/` : code source ou dépôts.
- `documents/` : documents client, specs, références.
- `generated/` : fichiers générés par les agents.
- `reports/` : rapports de tâches, audits, revues.
- `artifacts/` : livrables validés.
- `worktrees/` : worktrees Git isolés par agent.
- `memory/` : exports locaux de mémoire ou notes non sensibles.

## Règles obligatoires

1. Toujours identifier le projet comme `blockdevs`.
2. Ne jamais mélanger les informations avec un autre projet.
3. Lire ce fichier avant toute mission.
4. Consulter la mémoire projet via MCP avant toute décision importante.
5. Écrire les décisions durables dans la mémoire projet.
6. Distinguer fait confirmé, hypothèse, décision et information obsolète.
7. Ne pas publier, déployer, supprimer ou migrer sans validation humaine.
8. Produire un rapport final structuré à la fin de chaque tâche.

## Actions interdites sans validation humaine

- Déploiement production.
- Suppression de données.
- Migration base de données.
- Modification de secrets.
- Modification DNS / reverse proxy.
- Publication officielle.
- Envoi client final.
- Merge sur branche protégée.

## Format de rapport final

```text
PROJET:
TÂCHE:
AGENT:
CE_QUI_A_ÉTÉ_FAIT:
FICHIERS_MODIFIÉS:
COMMANDES_EXÉCUTÉES:
RÉSULTATS:
PREUVES:
RISQUES:
MÉMOIRE_À_METTRE_À_JOUR:
PROCHAINE_ACTION:
VALIDATION_HUMAINE_REQUISE:
```
```

---

## 10. Communication entre agents

### 10.1 Canaux

Les agents doivent communiquer par plusieurs couches :

```text
Kanban
  -> commentaires, handoffs, blocages, assignations

Swarm
  -> supervision live, workers, rôles

Mémoire projet MCP
  -> connaissances durables

Rapports de tâche
  -> ce qui a été fait, preuves, risques

delegate_task
  -> sous-agents temporaires pour analyses courtes

Fichiers de projet
  -> documents, livrables, rapports
```

### 10.2 Règle de rapport obligatoire

Chaque agent doit terminer une tâche avec :

```text
PROJET:
TÂCHE:
AGENT:
CE_QUI_A_ÉTÉ_FAIT:
FICHIERS_MODIFIÉS:
COMMANDES_EXÉCUTÉES:
RÉSULTATS:
PREUVES:
RISQUES:
DÉCISIONS:
MÉMOIRE_À_METTRE_À_JOUR:
PROCHAINE_ACTION:
VALIDATION_HUMAINE_REQUISE:
```

### 10.3 Handoff entre agents

Exemple :

```text
code-builder
  -> termine patch en worktree
  -> ajoute rapport Kanban
  -> assigne à code-reviewer

code-reviewer
  -> relit patch
  -> identifie risques
  -> si critique, assigne à code-reviewer-critical

code-reviewer-critical
  -> donne décision
  -> si OK, demande validation humaine avant merge
```

### 10.4 Apprentissage collectif

Les agents ne changent pas les poids des modèles. Ils “apprennent” par :

```text
- mémoire projet ;
- mémoire native de profil ;
- skills améliorées ;
- AGENTS.md ;
- SOUL.md ;
- rapports Kanban ;
- décisions validées ;
- corrections du sarl-governor.
```

---

## 11. Sous-agents temporaires

### 11.1 Règle

```text
delegate_task = sous-agent temporaire pour sous-tâche courte.
Kanban        = délégation durable entre agents/profils.
Swarm         = agents permanents supervisés.
```

### 11.2 Autorisations

| Profil | Peut créer des sous-agents ? | Commentaire |
|---|---:|---|
| `sarl-orchestrator` | Oui | max 3, contexte obligatoire |
| `sarl-orchestrator-critical` | Oui | pour audit ou comparaison |
| `research-sage` | Oui | recherche parallèle |
| `code-builder` | Oui | analyse tests/logs/modules |
| `qa-agent` | Oui | scénarios de tests |
| `docs-scribe` | Restreint | uniquement extraction/synthèse |
| `community-manager` | Restreint | brainstorming court |
| `support-agent` | Restreint | triage simple |
| `ops-foundation` | Très restreint | pas de prod/secrets |
| `codex-builder` | Non si runtime Codex | le runtime Codex peut limiter certains outils |

### 11.3 Limites

```yaml
subagents_policy:
  max_subagents_per_task: 3
  max_depth: 1
  no_secret_access: true
  no_production_access: true
  no_destructive_commands: true
  require_parent_context: true
  require_final_summary: true
```

---

## 12. Mémoire projet

### 12.1 Séparation des mémoires

```text
Mémoire native Hermes
  -> souvenirs propres à un profil/agent

PostgreSQL + pgvector via MCP
  -> mémoire métier partagée par projet
```

### 12.2 Project IDs

```text
sarl-agent-ai
blockdevs
salon-cinema
onmovecinema
ong-yerda
```

### 12.3 Types mémoire

```text
fact
hypothesis
decision
constraint
preference
technical_note
incident
solution
risk
meeting_summary
task_summary
handoff
report
deprecated
superseded
```

### 12.4 Statuts de vérité

```text
truth_status:
  hypothesis
  confirmed
  decision
  deprecated
  superseded
```

### 12.5 Schéma PostgreSQL cible

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL REFERENCES projects(id),
    type TEXT NOT NULL,
    truth_status TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT,
    source_path TEXT,
    source_url TEXT,
    created_by_profile TEXT,
    validated_by TEXT,
    confidence NUMERIC(3,2) DEFAULT 0.70,
    supersedes_id UUID NULL REFERENCES project_memory(id),
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_memory_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID REFERENCES project_memory(id) ON DELETE CASCADE,
    project_id TEXT NOT NULL REFERENCES projects(id),
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    token_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_project_memory_project
ON project_memory(project_id);

CREATE INDEX IF NOT EXISTS idx_project_memory_type
ON project_memory(project_id, type);

CREATE INDEX IF NOT EXISTS idx_project_memory_truth
ON project_memory(project_id, truth_status);

CREATE INDEX IF NOT EXISTS idx_project_memory_chunks_project
ON project_memory_chunks(project_id);
```

La dimension `vector(768)` est un exemple. Elle devra correspondre au modèle d’embedding réellement choisi.

### 12.6 Outils MCP requis

```text
project_context_get(project_id)
project_memory_search(project_id, query, type?, truth_status?)
project_memory_write(project_id, type, content, truth_status, source, confidence)
project_memory_decision_log(project_id)
project_memory_summary(project_id)
project_memory_supersede(project_id, old_memory_id, new_content)
project_memory_list_recent(project_id, limit)
project_memory_get(memory_id)
```

### 12.7 Règles mémoire

```text
- Toute mémoire doit avoir un project_id.
- Toute décision doit avoir truth_status=decision.
- Toute hypothèse doit rester truth_status=hypothesis.
- Une mémoire obsolète ne doit pas être supprimée sans raison : elle est marquée deprecated ou superseded.
- Les gros fichiers ne vont pas dans PostgreSQL.
- PostgreSQL stocke chemins, empreintes, fragments et embeddings.
```

---

## 13. MCP mémoire projet Python

### 13.1 Emplacement

```text
/root/CascadeProjects/SARL-agent-ai/services/project-memory-mcp/
```

### 13.2 Arborescence

```text
services/project-memory-mcp/
├── README.md
├── pyproject.toml
├── .env.example
├── src/
│   └── sarl_project_memory_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── db.py
│       ├── embeddings.py
│       ├── schemas.py
│       └── tools.py
├── migrations/
│   └── 001_init.sql
└── tests/
    ├── test_memory_write.py
    └── test_memory_search.py
```

### 13.3 Variables

```env
SARL_MEMORY_DATABASE_URL=postgresql://sarl_memory_user:CHANGE_ME@127.0.0.1:5432/sarl_agent_memory
SARL_MEMORY_EMBEDDING_PROVIDER=gemini
SARL_MEMORY_EMBEDDING_MODEL=text-embedding-004
SARL_MEMORY_ALLOWED_PROJECTS=sarl-agent-ai,blockdevs,salon-cinema,onmovecinema,ong-yerda
```

### 13.4 Configuration MCP conceptuelle Hermes

```yaml
mcp_servers:
  sarl_project_memory:
    command: "python"
    args:
      - "-m"
      - "sarl_project_memory_mcp.server"
    env:
      SARL_MEMORY_DATABASE_URL: "${SARL_MEMORY_DATABASE_URL}"
      SARL_MEMORY_EMBEDDING_PROVIDER: "${SARL_MEMORY_EMBEDDING_PROVIDER}"
      SARL_MEMORY_EMBEDDING_MODEL: "${SARL_MEMORY_EMBEDDING_MODEL}"
```

À adapter selon la manière dont le service sera lancé dans Docker ou sur l’hôte.

---

## 14. Structure hôte finale

```text
/root/CascadeProjects/SARL-agent-ai/
├── docker-compose.yml
├── .secrets/
├── workspace-runtime/
├── projects/
│   ├── blockdevs/
│   ├── salon-cinema/
│   ├── onmovecinema/
│   └── ong-yerda/
├── skills/
│   └── custom/
│       ├── sarl-agent-ai-operating-contract/
│       ├── sarl-routing-and-escalation/
│       ├── sarl-human-validation/
│       ├── sarl-project-memory-policy/
│       ├── sarl-agent-reporting/
│       ├── sarl-stack-stewardship/
│       └── sarl-security-guardrails/
├── services/
│   └── project-memory-mcp/
├── scripts/
│   ├── backup-hermes.sh
│   ├── restore-hermes.sh
│   ├── healthcheck.sh
│   ├── stack-update-plan.sh
│   └── create-project.sh
├── staging/
│   ├── stack-updates/
│   └── agent-generated-patches/
├── reports/
│   ├── stack-updates/
│   ├── governor/
│   ├── costs/
│   └── routing-tests/
├── backups/
│   ├── hermes/
│   ├── postgres/
│   ├── workspace/
│   ├── skills/
│   └── projects/
└── docs/
    ├── architecture.md
    ├── model-routing-policy.md
    ├── memory-policy.md
    ├── security-policy.md
    ├── agent-communication-policy.md
    └── runbooks/
```

---

## 15. Docker Compose : normalisation cible

### 15.1 Objectif

Remplacer le volume opaque Workspace pour les fichiers projet par un bind mount explicite :

```text
/root/CascadeProjects/SARL-agent-ai/projects -> /workspace
```

Monter aussi les skills custom :

```text
/root/CascadeProjects/SARL-agent-ai/skills/custom -> /opt/custom-skills:ro
```

### 15.2 Principe de modification

Ne pas supprimer l’ancien volume immédiatement. Procédure :

```text
1. Backup docker-compose.yml.
2. Backup volumes Docker.
3. Créer projects/ et skills/custom/.
4. Modifier Compose.
5. docker compose up -d.
6. Vérifier Workspace.
7. Vérifier que /workspace voit les projets.
8. Garder l’ancien volume comme rollback.
```

### 15.3 Exemple de bloc conceptuel

```yaml
services:
  hermes-workspace:
    volumes:
      - ./workspace-runtime:/app/runtime
      - ./projects:/workspace
      - ./skills/custom:/opt/custom-skills:ro

  hermes-agent:
    volumes:
      - hermes-agent-data:/opt/data
      - ./projects:/workspace
      - ./skills/custom:/opt/custom-skills:ro
```

Ce bloc est conceptuel : il faudra l’adapter au `docker-compose.yml` réel.

---

## 16. Skills custom

### 16.1 Emplacement

```text
/root/CascadeProjects/SARL-agent-ai/skills/custom/
```

### 16.2 Déclaration dans Hermes

```yaml
skills:
  external_dirs:
    - /opt/custom-skills
```

### 16.3 Skills à créer

```text
sarl-agent-ai-operating-contract
sarl-routing-and-escalation
sarl-human-validation
sarl-project-memory-policy
sarl-agent-reporting
sarl-stack-stewardship
sarl-security-guardrails
sarl-cost-control
sarl-governance-audit
```

### 16.4 Skill operating contract

```markdown
---
name: sarl-agent-ai-operating-contract
description: Contrat opérationnel commun pour tous les agents SARL-Agent-AI.
---

# SARL-Agent-AI Operating Contract

## Règles obligatoires

1. Toujours identifier le projet.
2. Toujours charger le contexte projet.
3. Toujours distinguer fait, hypothèse, décision et information obsolète.
4. Toujours produire un rapport final.
5. Toujours écrire les décisions importantes en mémoire projet.
6. Ne jamais mélanger les projets.
7. Ne jamais exécuter une action critique sans validation humaine.
8. Ne jamais lire ou modifier les secrets sauf profil explicitement autorisé.
9. Ne jamais déployer, supprimer, migrer ou publier sans validation.
10. En cas de doute, escalader.
```

### 16.5 Skill routing and escalation

```markdown
---
name: sarl-routing-and-escalation
description: Classification coût/risque et escalade vers les agents SARL.
---

# Routing and Escalation

## Niveaux

- SIMPLE
- STANDARD
- AVANCÉE
- CRITIQUE

## Règle

Si production, sécurité, DB, paiement, données personnelles, contrat, DNS, VPS,
publication officielle ou action irréversible : CRITIQUE.

## Sortie obligatoire

```text
PROJET:
NIVEAU:
RAISON:
AGENT_CIBLE:
MODÈLE_ATTENDU:
ACTION:
VALIDATION_HUMAINE:
```
```

### 16.6 Skill human validation

```markdown
---
name: sarl-human-validation
description: Politique de validation humaine obligatoire.
---

# Human Validation

## Actions bloquées sans validation

- docker compose down / pull / restart en production
- modification .env ou secrets
- migration PostgreSQL
- suppression de données
- déploiement production
- modification DNS / reverse proxy
- publication officielle
- envoi final client
- action financière
- action juridique

## Format de demande

```text
ACTION_DEMANDÉE:
POURQUOI:
RISQUES:
BACKUP_EXISTANT:
ROLLBACK:
TESTS:
VALIDATION_REQUISE:
```
```

---

## 17. SOUL.md des profils

### 17.1 `sarl-router`

```markdown
# sarl-router

Tu es le routeur économique de SARL-Agent-AI.

Tu ne réalises pas les missions longues. Tu classes les demandes.

Tu dois produire :

```text
PROJET:
NIVEAU:
RAISON:
AGENT_CIBLE:
ACTION_RECOMMANDÉE:
VALIDATION_HUMAINE:
```

Tu dois utiliser les modèles économiques. Si une demande semble critique, tu dois router vers `sarl-orchestrator-critical`.
```

### 17.2 `sarl-orchestrator`

```markdown
# sarl-orchestrator

Tu es l’orchestrateur normal de SARL-Agent-AI.

Tu coordonnes les agents, crées les tâches Kanban, consultes le contexte projet et la mémoire projet.

Tu dois utiliser les modèles économiques fiables.

Tu ne dois pas traiter seul les tâches critiques. Tu dois escalader vers `sarl-orchestrator-critical`.

Tu dois toujours :
- identifier le projet ;
- consulter AGENTS.md ;
- consulter la mémoire projet si nécessaire ;
- créer un plan ;
- déléguer ;
- demander des rapports ;
- vérifier les blocages ;
- produire une synthèse finale.
```

### 17.3 `sarl-orchestrator-critical`

```markdown
# sarl-orchestrator-critical

Tu es l’orchestrateur critique de SARL-Agent-AI.

Tu interviens seulement pour les tâches sensibles, avancées ou irréversibles.

Tu peux utiliser Claude, GPT ou un modèle premium fiable.

Tu dois :
- vérifier les risques ;
- vérifier les alternatives ;
- demander validation humaine ;
- interdire les actions dangereuses ;
- exiger backup et rollback ;
- produire une décision structurée.

Tu ne dois pas exécuter directement une action production sans validation humaine explicite.
```

### 17.4 `sarl-governor`

```markdown
# sarl-governor

Tu es l’agent de gouvernance.

Tu vérifies que les agents respectent :
- classification des tâches ;
- projet correct ;
- mémoire non mélangée ;
- validation humaine ;
- usage premium justifié ;
- rapports finaux ;
- règles de sécurité.

Tu produis des audits et alertes. Tu ne modifies pas la production.
```

### 17.5 `sarl-stack-steward`

```markdown
# sarl-stack-steward

Tu es l’agent de maintenance évolutive de la stack Hermes.

Tu surveilles la documentation officielle Hermes Agent et le dépôt hermes-workspace.
Tu compares la documentation à la configuration locale.
Tu proposes des mises à jour, patches ou améliorations.

Tu peux :
- lire la documentation ;
- analyser la stack ;
- préparer un rapport ;
- préparer un patch dans staging ;
- créer une tâche Kanban ;
- demander validation.

Tu ne dois jamais appliquer une modification critique sans validation humaine.
```

---

## 18. Kanban

### 18.1 Boards

```text
sarl-agent-ai     -> maintenance de la stack, gouvernance, évolution
blockdevs         -> projet BlockDevs
salon-cinema      -> projet Salon du Cinéma
onmovecinema      -> projet OnMoveCinema
ong-yerda         -> projet ONG Yerda
```

### 18.2 Colonnes recommandées

```text
Backlog
Ready
In Progress
Needs Review
Needs Human Approval
Blocked
Done
Archived
```

### 18.3 Règle d’assignation

```text
Tâche simple      -> agent économique
Tâche standard    -> agent métier
Tâche avancée     -> agent spécialisé + reviewer
Tâche critique    -> orchestrator-critical + validation humaine
Maintenance stack -> stack-steward + governor + humain
```

### 18.4 Template tâche Kanban

```markdown
# Tâche SARL-Agent-AI

## Projet
<project_id>

## Niveau
SIMPLE / STANDARD / AVANCÉE / CRITIQUE

## Objectif
...

## Contexte
...

## Agent assigné
...

## Modèle attendu
...

## Fichiers autorisés
...

## Interdictions
...

## Livrable attendu
...

## Validation humaine requise
Oui / Non
```

---

## 19. Swarm Workspace

### 19.1 Mapping rôles

| Rôle Swarm | Profile Hermes |
|---|---|
| Orchestrator | `sarl-orchestrator` |
| Custom / Router | `sarl-router` |
| Custom / Critical Orchestrator | `sarl-orchestrator-critical` |
| Builder | `code-builder` |
| Custom / Codex Builder | `codex-builder` |
| Reviewer | `code-reviewer` |
| Custom / Critical Reviewer | `code-reviewer-critical` |
| Sage | `research-sage` |
| Scribe | `docs-scribe` |
| QA | `qa-agent` |
| Foundation / Ops | `ops-foundation` |
| Custom / Governor | `sarl-governor` |
| Custom / Stack Steward | `sarl-stack-steward` |

### 19.2 Démarrage progressif

Phase 1 :

```text
sarl-router
sarl-orchestrator
research-sage
docs-scribe
```

Phase 2 :

```text
code-builder
code-reviewer
qa-agent
```

Phase 3 :

```text
sarl-orchestrator-critical
sarl-governor
sarl-stack-steward
```

Phase 4 :

```text
codex-builder
code-reviewer-critical
community-manager
support-agent
bureau-etudes-agent
designer-3d-agent
```

---

## 20. Bacs à sable

### 20.1 Rappel

Un profile n’est pas un sandbox.

```text
Profile = identité, config, mémoire, sessions, skills.
Sandbox = isolation d’exécution terminal/fichier.
```

### 20.2 Profils nécessitant sandbox fort

```text
code-builder
codex-builder
qa-agent
code-reviewer
ops-foundation
sarl-stack-steward
```

### 20.3 Règles sandbox

```text
- pas d’accès direct à /root hors chemins montés ;
- pas d’accès secrets sauf profil autorisé ;
- pas de production ;
- pas de docker compose down sans validation ;
- pas de migration DB sans backup ;
- pas de suppression ;
- worktree dédié pour code ;
- checkpoints activés.
```

### 20.4 Configuration conceptuelle

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: false
  docker_volumes:
    - "/workspace:/workspace"
```

À adapter selon la configuration réelle Hermes.

---

## 21. Git worktrees

### 21.1 Objectif

Éviter que plusieurs agents modifient le même checkout.

### 21.2 Structure

```text
projects/blockdevs/
├── source/
│   └── main-repo/
├── worktrees/
│   ├── code-builder/
│   ├── codex-builder/
│   ├── qa-agent/
│   └── reviewer/
```

### 21.3 Règles

```text
code-builder travaille dans worktrees/code-builder.
codex-builder travaille dans worktrees/codex-builder.
qa-agent travaille dans worktrees/qa-agent.
reviewer lit ou compare, mais ne merge pas sans validation.
```

---

## 22. Checkpoints et rollback

### 22.1 Objectif

Avant modification de fichiers, créer une possibilité de retour arrière.

### 22.2 Configuration conceptuelle

```yaml
checkpoints:
  enabled: true
```

### 22.3 Profils prioritaires

```text
code-builder
codex-builder
qa-agent
docs-scribe
community-manager
sarl-stack-steward
```

### 22.4 Règle

```text
Aucune modification importante sans checkpoint ou commit/worktree.
Aucune mise à jour stack sans backup complet.
```

---

## 23. Hooks de sécurité

### 23.1 Objectif

Transformer les règles de sécurité en blocages techniques.

### 23.2 Hook cible

```text
sarl-policy-guard
```

### 23.3 Actions à bloquer sans validation

```text
rm -rf
docker compose down
docker compose pull
docker compose up -d
systemctl stop
systemctl restart
ufw disable
modification .env
modification .secrets
DROP DATABASE
DROP TABLE
TRUNCATE
ALTER TABLE en production
migration sans backup
chmod 777
chown récursif sur /root
ouverture port public
modification nginx/apache/caddy
modification DNS
```

### 23.4 Logs du hook

```text
/root/CascadeProjects/SARL-agent-ai/reports/governor/security-hook.log
```

### 23.5 Politique

```text
Le prompt ne suffit pas.
Les actions critiques doivent être bloquées techniquement par hook ou procédure.
```

---

## 24. Validation humaine

### 24.1 Actions nécessitant validation

```text
- déploiement production ;
- suppression données ;
- migration base de données ;
- changement secrets ;
- changement DNS ;
- ouverture port public ;
- mise à jour stack ;
- changement docker-compose.yml ;
- modification reverse proxy ;
- publication officielle ;
- envoi client final ;
- réponse juridique ;
- action financière.
```

### 24.2 Format de demande

```text
ACTION:
PROJET:
RAISON:
RISQUES:
BACKUP:
ROLLBACK:
TESTS:
AGENT_DEMANDEUR:
AVIS_GOVERNOR:
VALIDATION_HUMAINE:
```

### 24.3 Réponse humaine attendue

```text
APPROUVÉ
REFUSÉ
APPROUVÉ AVEC CONDITIONS
DEMANDER PLUS D’INFOS
```

---

## 25. Gouvernance

### 25.1 `sarl-governor`

Rôle :

```text
- vérifier que les agents suivent les règles ;
- détecter les mélanges de projets ;
- détecter les actions critiques non escaladées ;
- détecter l’usage premium non justifié ;
- vérifier les rapports finaux ;
- produire des audits ;
- alerter l’humain.
```

### 25.2 Rapport hebdomadaire governor

```text
- nombre de tâches ;
- tâches critiques ;
- validations humaines ;
- incidents ;
- coûts premium ;
- erreurs de routage ;
- mémoires écrites ;
- projets actifs ;
- recommandations.
```

---

## 26. Maintenance évolutive de la stack

### 26.1 Agent dédié

```text
sarl-stack-steward
```

### 26.2 Mission

```text
Surveiller la documentation officielle Hermes Agent et hermes-workspace.
Comparer avec la stack locale.
Proposer des améliorations.
Préparer des patches en staging.
Créer des tâches Kanban.
Attendre validation humaine.
```

### 26.3 Workflow

```text
cron hebdomadaire
  |
  v
sarl-stack-steward lit docs officielles
  |
  v
compare stack locale
  |
  v
rapport dans reports/stack-updates/
  |
  v
patch éventuel dans staging/stack-updates/
  |
  v
tâche Kanban sarl-agent-ai
  |
  v
sarl-governor vérifie
  |
  v
humain valide
  |
  v
ops-foundation applique si autorisé
  |
  v
healthcheck + rollback si problème
```

### 26.4 Actions autorisées sans validation

```text
- lecture docs ;
- audit config ;
- rapport ;
- proposition ;
- patch staging ;
- tâche Kanban ;
- test non destructif.
```

### 26.5 Actions interdites sans validation

```text
- docker compose pull/up/down/restart ;
- modification compose ;
- modification .env ;
- modification secrets ;
- installation système ;
- migration DB ;
- suppression ;
- exposition publique ;
- mise à jour image en production.
```

---

## 27. Sécurité réseau

### 27.1 État actuel correct

```text
3000 lié à 127.0.0.1
8642 lié à 127.0.0.1
9119 non publié directement sur hôte
accès via tunnel SSH
```

### 27.2 Cible

```text
Tailscale privé
SSH en secours
Aucun port Hermes public
Pas de reverse proxy public en V1
Mot de passe Workspace conservé
```

### 27.3 Règle

```text
Ne pas exposer Workspace, Gateway ou Dashboard API directement sur Internet.
```

---

## 28. Secrets

### 28.1 Règles

```text
- ne jamais stocker les secrets dans projects/ ;
- ne jamais indexer .env dans la mémoire projet ;
- ne jamais donner les secrets aux sous-agents ;
- ne jamais lire .secrets sauf profil autorisé ;
- préférer secrets injectés côté Agent ;
- prévoir rotation régulière.
```

### 28.2 Profils autorisés à diagnostiquer les secrets

```text
ops-foundation
sarl-stack-steward
sarl-governor en lecture rapportée, pas extraction brute
```

### 28.3 Profils non autorisés

```text
community-manager
docs-scribe
research-sage
support-agent
designer-3d-agent
```

---

## 29. Coûts et budget

### 29.1 Principe

```text
Chaque appel premium doit avoir une raison.
Chaque escalade critique doit être traçable.
```

### 29.2 Journal premium

```text
reports/costs/premium-usage-YYYY-MM.md
```

Format :

```text
DATE:
PROJET:
AGENT:
MODÈLE:
RAISON:
NIVEAU:
TÂCHE:
APPROUVÉ_PAR:
```

### 29.3 Alertes

```text
- Claude/GPT utilisé trop souvent ;
- Codex utilisé pour tâche simple ;
- orchestrator-critical sollicité sans raison ;
- tâche simple non routée vers économique.
```

---

## 30. Backups

### 30.1 À sauvegarder

```text
docker-compose.yml
.secrets/
workspace-runtime/
volume hermes-agent-data
projects/
skills/custom/
services/project-memory-mcp/
PostgreSQL sarl_agent_memory
reports/
staging/
```

### 30.2 Dossiers backup

```text
/root/CascadeProjects/SARL-agent-ai/backups/
├── hermes/
├── postgres/
├── workspace/
├── skills/
└── projects/
```

### 30.3 Script conceptuel `backup-hermes.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
STAMP="$(date +%F_%H%M%S)"
BACKUP="$ROOT/backups"

cd "$ROOT"

mkdir -p "$BACKUP/hermes" "$BACKUP/workspace" "$BACKUP/projects" "$BACKUP/skills" "$BACKUP/postgres"

cp docker-compose.yml "$BACKUP/workspace/docker-compose.$STAMP.yml"

tar -czf "$BACKUP/projects/projects.$STAMP.tar.gz" projects || true
tar -czf "$BACKUP/skills/skills-custom.$STAMP.tar.gz" skills/custom || true
tar -czf "$BACKUP/workspace/workspace-runtime.$STAMP.tar.gz" workspace-runtime || true

docker compose ps > "$BACKUP/hermes/docker-ps.$STAMP.txt"
docker compose logs --tail=300 hermes-agent > "$BACKUP/hermes/hermes-agent.$STAMP.log"
docker compose logs --tail=300 hermes-workspace > "$BACKUP/hermes/hermes-workspace.$STAMP.log"

echo "Backup terminé: $STAMP"
```

À compléter avec dump PostgreSQL après création de la base mémoire.

---

## 31. Healthchecks

### 31.1 Commandes

```bash
cd /root/CascadeProjects/SARL-agent-ai

docker compose ps
curl -fsS http://127.0.0.1:8642/health
curl -fsS http://127.0.0.1:3000/api/sessions || true

docker compose logs --tail=100 hermes-agent
docker compose logs --tail=100 hermes-workspace

systemctl status postgresql --no-pager
```

### 31.2 Dashboard API

Le Dashboard API est dans le réseau Docker :

```text
http://hermes-agent:9119
```

Il n’est pas publié directement sur l’hôte. Pour le tester, utiliser `docker compose exec` depuis un conteneur qui peut le joindre, ou vérifier via Workspace.

---

## 32. Phases d’implémentation

### Phase 0 — Backup et gel de la stack

Objectif : ne rien casser.

```text
- copier docker-compose.yml ;
- sauvegarder volumes ;
- sauvegarder .secrets ;
- exporter logs ;
- documenter l’état actuel ;
- vérifier ports locaux.
```

### Phase 1 — Dossiers officiels

Créer :

```bash
cd /root/CascadeProjects/SARL-agent-ai

mkdir -p projects/{blockdevs,salon-cinema,onmovecinema,ong-yerda}
mkdir -p skills/custom
mkdir -p services/project-memory-mcp
mkdir -p reports/{stack-updates,governor,costs,routing-tests}
mkdir -p staging/{stack-updates,agent-generated-patches}
mkdir -p backups/{hermes,postgres,workspace,skills,projects}
mkdir -p scripts docs/runbooks
```

### Phase 2 — Bind mount `/workspace`

```text
- remplacer volume opaque Workspace par ./projects:/workspace ;
- monter ./skills/custom:/opt/custom-skills:ro ;
- redémarrer stack ;
- vérifier /workspace.
```

Rollback : restaurer l’ancien bloc volume.

### Phase 3 — Projets et contextes

Pour chaque projet :

```text
- créer AGENTS.md ;
- créer README.md ;
- créer project.yaml ;
- créer source/documents/generated/reports/artifacts/worktrees/memory.
```

### Phase 4 — Skills custom

Créer :

```text
sarl-agent-ai-operating-contract
sarl-routing-and-escalation
sarl-human-validation
sarl-project-memory-policy
sarl-agent-reporting
sarl-stack-stewardship
sarl-security-guardrails
sarl-cost-control
sarl-governance-audit
```

Déclarer `skills.external_dirs`.

### Phase 5 — Profiles de base

Créer progressivement :

```text
sarl-router
sarl-orchestrator
sarl-orchestrator-critical
research-sage
docs-scribe
```

Puis vérifier chaque profile.

### Phase 6 — Modèles

```text
- configurer router économique ;
- configurer orchestrator économique fiable ;
- préparer orchestrator-critical pour Claude/GPT ;
- préparer codex-builder pour Codex ;
- configurer auxiliaires économiques ;
- ajouter fallback_providers.
```

### Phase 7 — Kanban

```text
- créer board sarl-agent-ai ;
- créer boards projets ;
- créer templates tâches ;
- tester une tâche simple ;
- tester un handoff.
```

### Phase 8 — Swarm minimal

Démarrer seulement :

```text
sarl-router
sarl-orchestrator
research-sage
docs-scribe
```

Tester coordination.

### Phase 9 — PostgreSQL + pgvector

```text
- installer pgvector ;
- créer base sarl_agent_memory ;
- créer user dédié ;
- appliquer migrations ;
- tester insertion/recherche.
```

### Phase 10 — MCP mémoire Python

```text
- créer service Python ;
- connecter PostgreSQL ;
- exposer outils MCP ;
- déclarer MCP dans Hermes ;
- tester project_memory_write/search.
```

### Phase 11 — Sandbox, worktrees, checkpoints

```text
- configurer Docker backend ;
- créer worktrees ;
- activer checkpoints ;
- tester rollback.
```

### Phase 12 — Hooks de sécurité

```text
- créer hook sarl-policy-guard ;
- bloquer commandes dangereuses ;
- tester blocages ;
- journaliser événements.
```

### Phase 13 — Claude/Codex

```text
- intégrer credentials ;
- vérifier modèles exposés ;
- tester requête simple ;
- tester tâche critique ;
- activer profils premium ;
- surveiller coûts.
```

### Phase 14 — Agents avancés

Ajouter :

```text
code-builder
codex-builder
code-reviewer
code-reviewer-critical
qa-agent
ops-foundation
sarl-governor
sarl-stack-steward
community-manager
support-agent
bureau-etudes-agent
designer-3d-agent
```

### Phase 15 — Maintenance supervisée

```text
- cron hebdomadaire stack-steward ;
- rapport stack ;
- tâche Kanban de validation ;
- governor audit ;
- validation humaine ;
- application contrôlée.
```

---

## 33. Tests de routage obligatoires

### 33.1 Cas de test

| Demande | Niveau attendu | Agent attendu |
|---|---|---|
| Résume ce texte | SIMPLE | docs-scribe |
| Prépare un post LinkedIn | STANDARD | community-manager |
| Fais une veille IA | STANDARD | research-sage |
| Corrige ce bug Laravel | AVANCÉE | code-builder |
| Revois ce patch sécurité | CRITIQUE | code-reviewer-critical |
| Déploie en production | CRITIQUE | orchestrator-critical + humain |
| Supprime les anciennes données clients | CRITIQUE | orchestrator-critical + humain |
| Modifie les DNS | CRITIQUE | orchestrator-critical + humain |
| Analyse ce contrat | CRITIQUE ou AVANCÉE | orchestrator-critical si engagement |
| Crée une maquette 3D | STANDARD/AVANCÉE | designer-3d-agent |

### 33.2 Critères de validation

Pour chaque test :

```text
- projet détecté ;
- contexte AGENTS.md chargé ;
- niveau correct ;
- agent correct ;
- modèle approprié ;
- escalade si nécessaire ;
- validation humaine si nécessaire ;
- mémoire consultée si nécessaire ;
- rapport final produit.
```

---

## 34. Critères d’acceptation finale

La mise en place est considérée stable lorsque :

```text
- Workspace démarre sans projet chargé ;
- /workspace pointe vers ./projects ;
- les profiles de base existent ;
- router classe correctement 10/10 tests ;
- orchestrator crée tâches Kanban ;
- agents échangent via Kanban ;
- AGENTS.md est respecté ;
- mémoire projet écrit/lit par project_id ;
- pgvector fonctionne ;
- MCP mémoire répond ;
- sandbox fonctionne ;
- worktrees isolent les modifications ;
- checkpoints permettent rollback ;
- hooks bloquent actions dangereuses ;
- Claude/Codex sont actifs mais utilisés seulement en critique/avancé ;
- stack-steward produit un rapport sans appliquer automatiquement ;
- governor détecte au moins les erreurs simulées ;
- backup/restore a été testé.
```

---

## 35. Runbook : mise à jour stack supervisée

### 35.1 Préparation

```text
1. sarl-stack-steward lit docs officielles.
2. Il produit rapport.
3. Il prépare patch dans staging.
4. Il crée tâche Kanban.
5. sarl-governor vérifie.
6. Humain valide.
```

### 35.2 Application

```text
1. Backup.
2. Healthcheck initial.
3. Application patch.
4. Redémarrage contrôlé.
5. Healthcheck final.
6. Rapport.
```

### 35.3 Rollback

```text
1. Restaurer docker-compose.yml.
2. Restaurer volumes ou fichiers.
3. Redémarrer stack.
4. Vérifier ports.
5. Documenter incident.
```

---

## 36. Runbook : création d’un nouveau projet

```text
1. Créer dossier dans projects/<project_id>.
2. Créer AGENTS.md.
3. Créer project.yaml.
4. Créer board Kanban.
5. Créer entrée projects dans PostgreSQL.
6. Tester project_context_get.
7. Créer première tâche Kanban.
```

Script conceptuel :

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="/root/CascadeProjects/SARL-agent-ai"
PROJECT_ID="$1"

mkdir -p "$ROOT/projects/$PROJECT_ID"/{source,documents,generated,reports,artifacts,worktrees,memory}

cat > "$ROOT/projects/$PROJECT_ID/project.yaml" <<EOF
project_id: $PROJECT_ID
name: $PROJECT_ID
status: active
workspace:
  root: /workspace/$PROJECT_ID
memory:
  backend: sarl-project-memory-mcp
  project_id: $PROJECT_ID
kanban:
  board: $PROJECT_ID
EOF

cat > "$ROOT/projects/$PROJECT_ID/AGENTS.md" <<EOF
# Projet : $PROJECT_ID

## Règles
- Toujours identifier le projet comme $PROJECT_ID.
- Ne jamais mélanger avec un autre projet.
- Demander validation humaine pour action critique.
EOF
```

---

## 37. Runbook : incident agent

```text
1. Stopper ou mettre en pause l’agent dans Operations/Swarm.
2. Conserver logs et session.
3. sarl-governor analyse violation.
4. Corriger SOUL.md/skill/hook si nécessaire.
5. Rejouer test de routage.
6. Documenter incident.
```

---

## 38. Operations Workspace

Operations doit servir à :

```text
- voir les profiles ;
- vérifier Needs setup ;
- surveiller workers ;
- lancer doctor ;
- auditer sécurité ;
- voir usage modèles ;
- vérifier checkpoints ;
- lancer backup ;
- surveiller gateway.
```

Workspace est le cockpit, mais pas l’unique source de configuration.

---

## 39. Conductor

Conductor peut être utilisé pour les missions complexes :

```text
- campagne marketing complète ;
- audit projet ;
- développement fonctionnalité ;
- veille approfondie ;
- préparation rapport client.
```

Mais il ne doit pas être bloquant.

```text
Si Conductor indisponible :
  Swarm + Kanban doivent continuer à fonctionner.
```

---

## 40. Profile distributions

Quand les profils seront stables, créer des distributions privées.

Objectifs :

```text
- versionner les agents ;
- restaurer rapidement ;
- déployer ailleurs ;
- exclure secrets, sessions et mémoire ;
- contrôler les changements par Git.
```

Profils candidats :

```text
sarl-router
sarl-orchestrator
sarl-orchestrator-critical
sarl-governor
sarl-stack-steward
code-builder
research-sage
docs-scribe
qa-agent
```

---

## 41. Corrections à appliquer dans la configuration existante

### 41.1 `fallback_providers` vide

À corriger.

### 41.2 Ancien champ `provider: nous`

L’audit signale un ancien champ racine `provider: nous`. Il faudra le supprimer lors de la normalisation, après backup et vérification que `model.provider: openrouter` est bien utilisé.

### 41.3 Claude/Codex non opérationnels

À corriger dans une phase dédiée.

### 41.4 pgvector absent

À installer avant la mémoire sémantique.

### 41.5 Volume Workspace opaque

À remplacer par bind mount explicite après backup.

---

## 42. Fichiers finaux attendus

```text
/root/CascadeProjects/SARL-agent-ai/docker-compose.yml
/root/CascadeProjects/SARL-agent-ai/projects/<project_id>/AGENTS.md
/root/CascadeProjects/SARL-agent-ai/projects/<project_id>/project.yaml
/root/CascadeProjects/SARL-agent-ai/skills/custom/*/SKILL.md
/root/CascadeProjects/SARL-agent-ai/services/project-memory-mcp/
```

Dans Hermes :

```text
/opt/data/config.yaml
/opt/data/.env
/opt/data/skills
profiles/<profile>/SOUL.md
profiles/<profile>/config.yaml
```

Les chemins exacts de profiles dans le volume seront confirmés au moment de l’implémentation par inspection du volume Hermes.

---

## 43. Ordre de travail recommandé

```text
1. Backup complet.
2. Créer dossiers.
3. Bind mount projects/ et skills/custom/.
4. Créer AGENTS.md/project.yaml.
5. Créer skills custom.
6. Créer profiles de base.
7. Configurer modèles économiques.
8. Ajouter fallback providers.
9. Créer Kanban boards.
10. Démarrer Swarm minimal.
11. Tester routage.
12. Installer pgvector.
13. Créer MCP mémoire.
14. Activer sandbox/worktrees/checkpoints.
15. Ajouter hooks.
16. Activer Claude/Codex.
17. Ajouter agents avancés.
18. Activer stack-steward.
19. Activer governor.
20. Tests finaux.
```

---

## 44. Références officielles à relire avant implémentation

```text
Hermes Agent — Configuration
https://hermes-agent.nousresearch.com/docs/user-guide/configuration

Hermes Agent — Docker
https://hermes-agent.nousresearch.com/docs/user-guide/docker

Hermes Agent — Context Files
https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files

Hermes Agent — Web Dashboard
https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard

Hermes Agent — Profiles
https://hermes-agent.nousresearch.com/docs/user-guide/profiles

Hermes Agent — Models
https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models

Hermes Agent — MCP
https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp

Hermes Agent — Kanban
https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

Hermes Agent — Delegation
https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation

Hermes Agent — Cron
https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

Hermes Agent — Git Worktrees
https://hermes-agent.nousresearch.com/docs/user-guide/git-worktrees

Hermes Agent — Checkpoints and Rollback
https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints-and-rollback

Hermes Agent — Fallback Providers
https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers

Hermes Agent — Profile Distributions
https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions

Hermes Agent — Security
https://hermes-agent.nousresearch.com/docs/user-guide/security

Hermes Workspace
https://github.com/outsourc-e/hermes-workspace
```

---

## 45. Conclusion

Cette architecture permet à SARL-Agent-AI de fonctionner comme une vraie équipe numérique :

```text
- plusieurs projets ;
- mémoire dédiée par projet ;
- agents spécialisés ;
- communication durable ;
- sous-agents temporaires ;
- orchestration économique ;
- escalade premium uniquement si nécessaire ;
- sandbox et rollback ;
- gouvernance ;
- maintenance évolutive supervisée.
```

La stack peut évoluer presque seule, mais seulement dans ce cadre :

```text
observer
analyser
proposer
préparer
tester
documenter
demander validation
appliquer seulement après autorisation
vérifier
rollback si problème
```

C’est la configuration cible avancée, robuste et fonctionnelle recommandée pour SARL-Agent-AI.
