# Tests profiles et routage - 18 juin 2026

## Configuration validee

| Profile | Primaire | Fallback 1 | Fallback 2 |
|---|---|---|---|
| `sarl-router` | OpenRouter `poolside/laguna-m.1:free` | Gemini `gemini-2.5-flash` | OpenRouter `auto` |
| `sarl-orchestrator` | DeepSeek `deepseek-chat` | Gemini `gemini-2.5-flash` | OpenRouter `auto` |
| `sarl-orchestrator-critical` | DeepSeek `deepseek-reasoner` | OpenRouter `auto` | Gemini `gemini-2.5-flash` |
| `research-sage` | Gemini `gemini-2.5-flash` | DeepSeek `deepseek-chat` | OpenRouter `auto` |
| `docs-scribe` | OpenRouter `poolside/laguna-m.1:free` | Gemini `gemini-2.5-flash` | OpenRouter `auto` |

Claude et OpenAI ne sont pas actives. Le profile critique reste donc une
configuration provisoire et ne doit pas executer d'action critique.

## Resultats

```text
sarl-router                 ROUTER_OK
sarl-orchestrator           ORCHESTRATOR_OK
sarl-orchestrator-critical  CRITICAL_OK
research-sage               RESEARCH_OK
docs-scribe                 DOCS_OK
```

Un premier test critique a tente un appel outil invalide. Un second test
explicitement sans outil a reussi. Ce point reste a retester apres activation
du modele premium cible.

## Skills

Les neuf skills `sarl-*` sont presents dans l'index du prompt de
`sarl-router`. Les permissions du bind mount ont ete corrigees pour permettre
la lecture par l'utilisateur `hermes`.

## Kanban

Board : `sarl-agent-ai`

Tache de preuve : `t_d20204ff`

```text
creation -> commentaire sarl-router -> reassignation docs-scribe
-> commentaire docs-scribe -> complete
resultat: KANBAN_HANDOFF_OK
worker demarre: non
```

## Swarm minimal

Roster charge :

```text
sarl-router
sarl-orchestrator
research-sage
docs-scribe
```

Les gateways de ces profiles restent arretees. Le profil `default` reste seul
gateway actif. Le healthcheck final rapporte zero session active.
