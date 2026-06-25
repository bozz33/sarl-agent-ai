# Reconstruction de `sarl/hermes-workspace`

## État : source-reproductible ✅

L'image en production `sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse`
(hermes-workspace **v2.3.0**) = upstream `outsourc-e/hermes-workspace` au commit
**`d04e1f3`** + le jeu de patches SARL, **désormais versionné** dans `patches/`.

Le `Dockerfile` clone l'upstream au commit épinglé, applique `patches/*.patch`,
puis `pnpm install --frozen-lockfile && pnpm build`.

## Build

```bash
docker build -t sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse deploy/hermes-workspace
```

Build volontairement **hors `docker-compose`** : un `docker compose up --build`
écraserait l'image en production sans contrôle. Reconstruire explicitement, tester,
puis retaguer.

## Patch SARL

`patches/sarl13-no-global-sse.patch` (30 fichiers, vs `d04e1f3`) :

- **no-global-sse** — suppression du flux SSE global (`send-stream.ts`,
  `terminal-stream.ts`, `use-streaming-message.ts`) → corrige pages blanches /
  buffering derrière Cloudflare.
- **suivi des missions de chat** — `chat-work-tracking.ts`, `approvals.$runId.$action.ts`,
  `profile-mcp-registry.ts`, traçage borné, proxy dashboard Kanban.

Récupéré depuis `backups/hermes/20260622T062058Z/project-files.tar.gz`
(working tree du clone, HEAD = `d04e1f3`). Validé : s'applique proprement sur un
upstream `d04e1f3` vierge.

Régénérer le patch après modification du clone :
`git -C <clone> add -A && git -C <clone> diff --cached d04e1f3 > patches/sarl13-no-global-sse.patch`

## Reprise immédiate (DR)

L'image sauvegardée reste un secours rapide :

```bash
sudo ./scripts/backup-hermes.sh --consistent --with-images
docker load -i backups/<horodatage>/images/hermes-workspace-image.tar
```
