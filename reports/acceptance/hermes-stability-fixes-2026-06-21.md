# Rapport de stabilisation Hermes — 21 juin 2026

## Projet

SARL-Agent-AI / Hermes Workspace

## Incident observé

- Interface parfois figée ou lente.
- Réponse agent terminée côté backend mais absente dans le chat.
- Accumulation de listeners SSE (`MaxListenersExceededWarning`).
- Requêtes répétées vers un endpoint runtime indisponible.
- Gateway de profil spécialisé démarré en parallèle du gateway principal.
- OpenRouter utilisé en premier, provoquant une erreur 402 avant fallback.
- Route de configuration non authentifiée transformée en erreur HTTP 500.

## Causes confirmées

1. Deux timers heartbeat étaient créés pour un flux de chat; un timer n'était jamais libéré.
2. Le flux Terminal ne nettoyait pas complètement ses listeners lors de l'annulation.
3. L'adaptateur HTTP ne propageait pas la fermeture client au `Request.signal`.
4. L'interface ignorait une réponse achevée si la connexion SSE semblait encore active.
5. Les réponses terminées n'étaient pas exposées par l'endpoint `active-run`.
6. Les 404 runtime étaient interrogées sans cache négatif.
7. Le profil actif persistant `sarl-stack-steward` lançait un second gateway au redémarrage.
8. Le handler Hermes config retournait le booléen `false` au framework au lieu d'une réponse 401.
9. Le modèle racine était `openrouter/auto`, contrairement à la politique coût/fiabilité du document.

## Correctifs appliqués

- Heartbeat SSE unique et nettoyage des timers/listeners.
- Annulation explicite des flux Terminal et propagation de l'abandon HTTP.
- Récupération côté chat de la dernière réponse terminée.
- Endpoint active-run étendu avec `latestRun`.
- Cache négatif de 60 secondes pour les endpoints runtime 404/405.
- Réponse HTTP 401 correcte pour `/api/claude-config`.
- En-têtes de sécurité ajoutés à Workspace.
- Profil actif remis à `default`; seul le gateway principal démarre.
- Modèle principal réglé sur `gemini-3.1-flash-lite`.
- Fallbacks : `deepseek-chat`, puis `openrouter/auto`.
- Champs racine obsolètes `provider` et `base_url` supprimés par le script de normalisation.
- Image déployée : `sarl/hermes-workspace:d04e1f3-sarl7`.

## Backup et rollback

- Backup vérifié :
  `/root/CascadeProjects/SARL-agent-ai/backups/hermes/20260620T120204Z`
- Vérification de restauration : `BACKUP_RESTORE_VERIFY_OK`.
- Rollback : remettre l'ancien tag Workspace dans `docker-compose.yml`, puis recréer `hermes-workspace`.

## Preuves de validation

- Build client et SSR : réussi.
- Tests ciblés : 13/13 réussis.
- Healthcheck complet après déploiement : réussi.
- Services restés sains pendant environ huit heures.
- Test navigateur chat : réponse `FINAL_OK` visible.
- Modèle affiché : `gemini-3.1-flash-lite`.
- Test navigateur Terminal : terminal actif, aucune requête HTTP 500.
- `/api/claude-config` non authentifié : HTTP 401, plus de 500.
- Charge HTTP : 100/100 réponses HTTP 200 sur Workspace; test précédent 200/200 sur Workspace + Gateway.
- Logs finaux : aucun `MaxListenersExceededWarning`, `Internal Server Error`, `Stream error` ou `Request error`.
- Processus : un seul `hermes gateway run`.
- Repos final :
  - Agent : environ 0,5 % CPU, 655 MiB.
  - Workspace : environ 0,1 % CPU, 216 MiB.

## Conclusion

Les symptômes reproduits de gel, réponse vide et lenteur ne provenaient pas d'une saturation du VPS. Ils provenaient principalement de fuites de flux/listeners, d'une récupération incomplète des réponses terminées, d'un gateway concurrent et d'un routage modèle sous-optimal.

La plateforme est stable pour les scénarios testés. L'absence absolue de bugs ne peut pas être garantie; une surveillance continue et des tests de durée restent nécessaires avant de déclarer une stabilité de production complète.

## Validation humaine

La demande utilisateur autorisait explicitement la correction et le déploiement. Aucun port public, secret, DNS, schéma de base de données ou donnée métier n'a été modifié.
