# Phase 2 - Journal d'implementation

Date de debut : 18 juin 2026

Source : `SARL-Agent-AI-document-complet-v1.3.md`

## Backup pre-phase

```text
/root/SARL-agent-ai-rollback/pre-phase2-20260618T144910Z
```

Contenu :

- projet et secrets ;
- volumes Hermes ;
- images Docker exactes ;
- metadata, logs et healthchecks ;
- dump PostgreSQL ;
- checksums SHA-256 ;
- script autonome de rollback.

## Palier 1

Etat :

- arborescence officielle creee ;
- dossier `projects/` cree et monte sur `/workspace` ;
- aucun projet cree ou charge ;
- aucun worker projet automatique ;
- neuf skills custom crees ;
- scripts backup, restore, healthcheck et creation projet crees ;
- aucun profil nouveau lance ;
- aucune base PostgreSQL creee ;
- aucun MCP active.

## Regle de progression

Chaque palier doit passer :

1. validation syntaxique ;
2. healthcheck Docker ;
3. verification Workspace ;
4. preuve de rollback ;
5. rapport avant palier suivant.

## Etat detaille

| Lot | Etat | Preuve ou reste |
|---|---|---|
| Backup pre-phase 2 | Termine | Archives projet, volumes, images, PostgreSQL et SHA-256 valides |
| Runbook rollback | Prepare | Script cree, restauration destructive non executee |
| Caveman | Termine | Installe dans `.agents/skills` |
| Arborescence phase 2 | Termine | `skills`, `services`, `scripts`, `reports`, `staging`, `backups`, `docs` |
| Dossier projets | Termine | `projects/` monte sur `/workspace`, actuellement vide |
| Bind mount projets | Termine | Agent et Workspace voient `/workspace` |
| Bind mount skills custom | Termine | Agent et Workspace voient `/opt/custom-skills` |
| Skills custom | Termine | Neuf skills lisibles par `hermes` et presents dans l'index du prompt |
| Scripts exploitation | Partiel | Scripts syntaxiquement valides; healthcheck non-root renforce; restore complet non teste |
| Profiles SARL | Termine | Cinq profiles phase 5 crees, decrits, configures et testes |
| Routage et fallback | Termine pour providers actifs | Primaires et doubles fallbacks configures; Claude/OpenAI attendent leurs credentials |
| Kanban | Termine pour socle | Board interne cree et handoff routeur vers docs teste sans worker |
| Swarm phase 2 | Termine pour socle minimal | Roster quatre profiles charge; aucune gateway profile demarree |
| PostgreSQL/pgvector | Termine pour socle DB | pgvector 0.6.0 installe; base/role dedies et schema migre; zero projet et zero memoire |
| MCP memoire Python | Termine | Service 0.2.0 sain, recherche hybride Gemini/pgvector 768D, pool partage sans fuite, 8 outils connectes aux 17 profils |
| Sandbox/worktrees/checkpoints | Termine pour le socle | Daemon Docker dedie actif, image approuvee prechargee, worktree et rollback testes |
| Hooks securite | Termine pour les profils actifs | `sarl-policy-guard` monte en lecture seule, teste 6/6, approuve et valide sur 17 profils |
| Claude/Codex | Non commence | Credentials Hermes toujours manquants |
| Agents avances | Partiel avance | Dix profils economiques avances/metier crees et testes; deux premium restent inactifs |
| Tailscale | Non commence | Acces SSH conserve |
| Tests acceptation finale | Termine hors dependances externes | `SARL_ACCEPTANCE_OK`, appels modeles 15/15, sandbox agents 2/2, routage 10/10, Kanban et restauration isolee valides |

## Paliers suivants

1. PostgreSQL/pgvector puis MCP memoire.
2. Sandbox, worktrees, checkpoints et hooks.
3. Activation Claude/Codex et agents avances.

## Palier 2 - Profiles de base

Crees le 18 juin 2026 :

```text
sarl-router
sarl-orchestrator
sarl-orchestrator-critical
research-sage
docs-scribe
```

Preuves :

- profiles crees via CLI Hermes officielle ;
- descriptions de routage renseignees ;
- `SOUL.md` dedies installes ;
- 73 skills Hermes disponibles par profile ;
- gateways des cinq profiles arretees ;
- profil `default` conserve actif et non remplace ;
- healthcheck global valide ;
- zero session active.

Validation :

- modeles economiques attribues ;
- doubles fallbacks configures ;
- profile critique provisoire clairement documente ;
- skills custom visibles dans l'index du prompt ;
- test conversationnel reussi pour chaque profile ;
- gateways des profiles toujours arretees ;
- profil `default` conserve actif.

Rapport :

`reports/routing-tests/phase2-profiles-2026-06-18.md`

## Palier 3 - Kanban et Swarm minimal

- board `sarl-agent-ai` cree ;
- tache de preuve `t_d20204ff` creee en etat bloque ;
- commentaire de routage ajoute ;
- handoff vers `docs-scribe` teste ;
- tache cloturee avec `KANBAN_HANDOFF_OK` ;
- aucun worker lance pendant le test ;
- roster Swarm reduit a `sarl-router`, `sarl-orchestrator`,
  `research-sage` et `docs-scribe` ;
- anciennes declarations `swarm1` a `swarm6` retirees du roster ;
- profiles historiques conserves arretes pour rollback ;
- healthcheck global valide avec zero session active.

## Corrections techniques trouvees pendant les tests

1. `groq` n'est pas accepte comme provider principal par ce runtime Hermes,
   bien qu'il fonctionne pour les modeles auxiliaires. Routeur et docs utilisent
   donc OpenRouter.
2. Les fichiers de logs crees lors du premier test appartenaient a `root`.
   Permissions corrigees pour `hermes`.
3. Le bind mount des skills custom existait mais n'etait pas lisible par
   `hermes`. Permissions corrigees.
4. Le healthcheck testait les mounts en root et donnait un faux positif. Il
   verifie maintenant les acces avec les utilisateurs applicatifs.

## Palier 4 - Memoire projet, preparation

Service cree :

`services/project-memory-mcp/`

Contenu :

- package Python et environnement virtuel local ;
- MCP SDK stable `1.28.0` borne a `<2` ;
- psycopg `3.3.4` et pool `3.3.1` ;
- huit outils MCP requis ;
- allowlist stricte `project_id` ;
- refus des contenus et chemins ressemblant a des secrets ;
- contraintes decision/hypothese ;
- recherche lexicale isolee par projet ;
- migration PostgreSQL avec pgvector ;
- rollback SQL ;
- 9 tests unitaires valides ;
- import serveur FastMCP valide.

Execute apres validation :

- backup PostgreSQL avec SHA-256 ;
- installation `postgresql-16-pgvector` 0.6.0 ;
- creation role `sarl_memory_user` ;
- creation base `sarl_agent_memory` ;
- secret dedie permissions `0600` ;
- application migration ;
- test PostgreSQL ecriture/recherche/lecture/supersession ;
- nettoyage du projet et des memoires de test ;
- verification finale : zero projet, zero memoire, zero chunk ;
- image `sarl/project-memory-mcp:0.1.1` construite.

Activation runtime validee :

- regle `pg_hba.conf` dediee au socket local ;
- reload PostgreSQL sans restart ;
- service MCP ajoute a Docker Compose ;
- aucun port hote publie ;
- 5 profiles connectes ;
- 8 outils decouverts sur chaque profile ;
- agent orchestrateur ecrit puis recherche une memoire ;
- `project_id` interdit refuse ;
- donnees test nettoyees ;
- base finale vide.

Complete :

- embeddings semantiques Gemini en 768 dimensions ;
- recherche hybride lexicale et cosinus avec repli lexical ;
- MCP active sur les dix-sept profils.

Runbook :

`docs/runbooks/activate-project-memory.md`

Patch prepare :

`staging/stack-updates/project-memory-activation.md`

## Palier 5 - Isolation et garde-fous

Realise :

- hook `sarl-policy-guard.py` ;
- 6 tests unitaires ;
- activation pilote `docs-scribe` ;
- consentement Hermes et allowlist ;
- `hermes hooks doctor` valide ;
- commande critique bloquee ;
- commande sure autorisee ;
- journal JSONL ;
- checkpoints actives sur `docs-scribe` ;
- snapshot, diff et rollback reels dans `/tmp` ;
- helper worktree avec validation stricte ;
- test worktree reel puis nettoyage ;
- dossier projets toujours vide.

Sandbox Docker :

- Docker CLI presente dans Hermes ;
- socket hote volontairement absent ;
- daemon Docker-in-Docker dedie actif sur reseau interne ;
- controle via socket Unix partage, sans API TCP 2375 ;
- image Python 3.11 / Node.js 20 prechargee par digest ;
- workflows reels `code-builder` et `qa-agent` valides ;
- aucun pull arbitraire pendant les missions.

## Palier 9 - Finalisation sans projet

- checkpoints, hook et MCP generalises aux 17 profils ;
- ancien champ racine `provider` retire des configurations actives ;
- `hermes doctor --fix` execute sur les profils economiques actifs ;
- deux crons hebdomadaires crees pour stack-steward et governor ;
- timer systemd actif pour leurs ticks sans gateway profile permanente ;
- 17 profils exportes avec checksums ;
- workflow Kanban temporaire cree, handoff valide puis archive ;
- routeur rejoue et valide 10/10 ;
- campagne technique : `SARL_ACCEPTANCE_OK` ;
- campagne modeles : `MODEL_WORKFLOW_SMOKE_OK`.

## Stabilisation Workspace - 19 juin 2026

Problemes confirmes :

- environ 80 PTY de suivi de logs dupliques, soit pres de 165 processus ;
- avertissements Node `MaxListenersExceededWarning` ;
- selection des profils premium sans credentials, causant attente puis echec
  Codex avant fallback ;
- OpenRouter gratuit utilise sur des profils interactifs et temps de reponse
  eleves ;
- assets Workspace non compresses : environ 2,65 Mio au chargement initial ;
- 97 connexions PostgreSQL idle creees par les sessions MCP.

Corrections :

- purge Workspace et timer `sarl-workspace-janitor.timer` toutes les dix
  minutes ;
- profils premium configurables en mode provisoire DeepSeek ;
- profil par defaut et profils rapides sur Gemini 3.1 Flash Lite ;
- retries limites a 1, timeouts reduits, sondes de contexte coupees sur les
  profils simples ;
- Workspace construit depuis le commit officiel `d04e1f3` ;
- compression gzip des assets statiques ;
- MCP 0.2.0 avec un seul pool PostgreSQL partage et embeddings Gemini
  `gemini-embedding-001` normalises en 768 dimensions ;
- cache memoire des assets immuables Workspace ;
- lecture locale prioritaire et cache de 2 secondes pour les profils.

Mesures :

```text
Workspace avant : ~480 Mio, ~165 processus
Workspace apres : ~160-200 Mio, 2 processus applicatifs au repos
Bundle principal avant : 2,25 Mio
Bundle principal gzip : 683 Kio
Profil par defaut avant : environ 16-23 s selon routage OpenRouter
Profil par defaut apres : environ 7-8 s
Connexions PostgreSQL avant : 97 idle applicatives
Apres 100 sessions MCP : 1 idle applicative
Liste profils : 2,09 s avant, 5-8 ms pour les appels en rafale apres cache
Bundle statique : 58 ms avant, 31 ms apres cache (mediane, charge c10)
```

Restent conditionnes a une action externe :

- authentification Claude/OpenAI-Codex ;
- connexion Tailscale ;

Aucun projet metier n'a ete cree. `projects/` reste vide hors `.gitkeep`.

Rapport :

`reports/governor/isolation-tests-2026-06-18.md`

## Palier 6 - Agents avances economiques

Crees, configures et testes :

```text
sarl-governor
sarl-stack-steward
code-builder
code-reviewer
qa-agent
ops-foundation
```

Tous possedent :

- description de routage ;
- `SOUL.md` dedie ;
- modele primaire et doubles fallbacks ;
- checkpoints actifs ;
- hook securite valide ;
- gateway arretee.

`code-builder` et `qa-agent` ont backend Docker mais restent fail-closed tant
que le daemon sandbox dedie n'existe pas.

Rapport :

`reports/routing-tests/advanced-profiles-2026-06-18.md`

## Palier 7 - Agents metier

Crees et testes :

```text
community-manager
support-agent
bureau-etudes-agent
designer-3d-agent
```

Aucun canal externe n'est configure. Aucune publication ou communication
automatique. Gateways arretees.

Rapport :

`reports/routing-tests/business-profiles-2026-06-18.md`

## Palier 8 - Routage et gouvernance

- premier test routeur rejete : agents inventes et classifications incorrectes ;
- identite routeur corrigee avec table canonique ;
- modele routeur passe a Gemini Flash ;
- 10 cas obligatoires rejoues ;
- score final : `10/10` ;
- `AGENTS.md` temporaire charge et respecte (`AGENTS_CONTEXT_OK`) ;
- fixture supprimee, dossier projets revenu vide ;
- orchestrateur cree lui-meme la carte Kanban `t_1873c36d` ;
- carte bloquee puis archivee sans worker ;
- governor detecte quatre violations simulees ;
- governor ne repete pas le secret ;
- stack-steward produit etat/ecarts/risques/patch ;
- stack-steward confirme `APPLIQUE: non`.

Rapports :

- `reports/routing-tests/router-10-cases-2026-06-18.md`
- `reports/governor/governor-steward-tests-2026-06-18.md`

## Correction demandee

Les contextes temporaires `blockdevs`, `salon-cinema`, `onmovecinema`,
`ong-yerda` et `sarl-agent-ai` ont ete retires. `/workspace` reste vide jusqu'a
creation explicite d'un projet par l'administrateur.
