# Stabilite et performances Workspace - 19 juin 2026

## Causes confirmees

1. Workspace accumulait des processus `pty-helper.py` et `tail -F` pour les
   journaux des profils. Plusieurs watchers identiques restaient ouverts.
2. Node signalait une accumulation de listeners.
3. La selection de `codex-builder` ou `code-reviewer-critical` utilisait des
   profils sans configuration complete et provoquait des erreurs
   d'authentification.
4. Les profils interactifs utilisaient des modeles plus lents ou des files
   OpenRouter gratuites.
5. Les assets frontend n'etaient pas compresses.
6. Chaque session MCP pouvait initialiser un nouveau pool PostgreSQL. La base
   a atteint 97 connexions idle et depasse `max_connections=100`.
7. `/api/profiles/list` interrogeait le dashboard avant le volume local et
   prenait environ 2,09 secondes.
8. Les bundles immuables etaient relus et recompresses a chaque requete.

## Corrections appliquees

- Workspace officiel commit `d04e1f3` construit et deploye.
- Patch local gzip et cache memoire des assets statiques immuables.
- Lecture locale prioritaire et cache de deux secondes pour les profils.
- Timer `sarl-workspace-janitor.timer` actif.
- Profils premium en mode provisoire DeepSeek Reasoner.
- Default/router/docs et profils rapides sur Gemini 3.1 Flash Lite.
- Fallbacks et retries raccourcis.
- MCP memoire 0.2.0 avec pool singleton, maximum trois connexions, recherche
  hybride et embeddings Gemini 768D.

## Resultats

```text
SARL_ACCEPTANCE_OK
MODEL_WORKFLOW_SMOKE_OK
ROUTING_10_10 (3 repetitions consecutives)
```

Stress et performances :

```text
100 ouvertures de session MCP, p95 922 ms
1 connexion PostgreSQL applicative idle finale
API Hermes : 12 941 requetes / 20 s, zero erreur
Workspace : 8 172 requetes / 20 s, 7 timeouts a 50 connexions (0,086 %)
Bundle mediane : 58 ms avant, 31 ms apres cache
Liste profils : 2,09 s avant, puis 5-8 ms pour les appels en rafale
5 agents concurrents : 17,2 s, cinq reponses correctes
```

Le dossier `projects/` reste vide hors `.gitkeep`.
