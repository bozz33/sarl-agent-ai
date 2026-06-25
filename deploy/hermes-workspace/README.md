# Reconstruction de `sarl/hermes-workspace`

## État

L'image en production `sarl/hermes-workspace:d04e1f3-sarl13-no-global-sse`
(hermes-workspace **v2.3.0**) a été construite à partir de l'upstream
`outsourc-e/hermes-workspace` au commit **`d04e1f3`**, plus des patches SARL.

L'image embarque uniquement le build (`/app/dist`, `server-entry.js`) — **pas les
sources ni les patches**. La source-repro exacte n'est donc pas possible en l'état.

## Ce que fournit ce dossier

`Dockerfile` reconstruit une base **vanille** de l'upstream au commit épinglé :

```bash
docker build -t sarl/hermes-workspace:rebuild deploy/hermes-workspace
```

Build volontairement **hors `docker-compose`** : un `docker compose up --build`
écraserait l'image patchée en production et réintroduirait le SSE global.

## Patches SARL manquants (à récupérer)

Le suffixe de tag `sarl13-no-global-sse` désigne le jeu de patches SARL appliqué
sur l'upstream :

- **no-global-sse** — suppression du flux SSE global (cause de pages blanches /
  buffering derrière Cloudflare).
- suivi borné / activity-bounded, janitor PTY (cf. itérations `sarl4`…`sarl13`).

Ces patches ne sont pas versionnés ici (perdus avec le clone de travail). Pour
reproduire l'image exacte :

1. Récupérer le diff vs `d04e1f3` (depuis une éventuelle sauvegarde du clone, ou
   en re-dérivant les modifications).
2. Le déposer en `patches/*.patch` (appliqué automatiquement par le Dockerfile).
3. Rebuild + retag `d04e1f3-sarl13-no-global-sse`.

## Reprise immédiate (DR)

Tant que les patches ne sont pas récupérés, l'**image construite reste l'artefact
de référence**. Sauvegarde / restauration :

```bash
sudo ./scripts/backup-hermes.sh --consistent --with-images
docker load -i backups/<horodatage>/images/hermes-workspace-image.tar
```
