# Sandbox, worktrees, checkpoints et hooks

Etat : daemon sandbox et garde-fou actifs. L'image d'execution
`sarl/sandbox-runtime:python3.11-nodejs20-playwright` est prechargee et le
reseau de controle reste volontairement interne.

## Decisions

- profils direction/recherche/documentation : terminal local limite, aucun
  acces Docker socket ;
- futurs profils code/QA : backend Docker obligatoire ;
- futurs profils ops : profil separe, commandes critiques bloquees ;
- aucun projet charge : aucun worktree permanent cree ;
- worktrees crees seulement avec un projet Git explicite ;
- checkpoints actives sur profils qui ecrivent des fichiers ;
- hook `sarl-policy-guard` active apres consentement explicite.

## Hook prepare

```text
hooks/sarl-policy-guard.py
```

Blocages :

- suppression recursive ;
- Docker Compose down/pull/up ;
- arret/restart service ;
- firewall disable/flush ;
- DROP/TRUNCATE/ALTER TABLE ;
- ecriture `.env`/`.secrets` ;
- chmod 777 ;
- chown recursif racine ;
- ecoute publique ;
- configuration webserver/DNS.

## Activation

Le dossier `./hooks` est monte en lecture seule dans `hermes-agent` sous
`/opt/sarl-hooks`. Le hook est declare dans les profils actifs, approuve par
le mecanisme de consentement Hermes et controle avec `hermes hooks doctor`.
Les commandes sures sont autorisees et les actions critiques sont bloquees.

## Worktrees

Aucun worktree sans depot projet. Lors de creation d'un projet :

```text
source/<repo>
worktrees/code-builder
worktrees/codex-builder
worktrees/qa-agent
worktrees/reviewer
```

Chaque worktree utilise une branche dediee. Aucun merge automatique.

Helper : `scripts/create-worktree.sh`.

Il refuse tout chemin hors de la racine officielle, valide agent/branche et
refuse d'ecraser un worktree existant.

## Daemon sandbox

Patch prepare :

```text
staging/stack-updates/docker-compose.sandbox.yml
staging/stack-updates/sandbox-activation.md
```

Le patch est applique. Docker-in-Docker est prive, sans montage du socket
Docker hote. Hermes communique avec lui par le socket Unix partage
`/opt/sandbox-shared/docker.sock`; aucun port TCP Docker n'est utilise. Le
reseau `sandbox-control` est interne : le daemon ne telecharge pas d'image a
l'execution. L'image Python/Node/Playwright approuvee est prechargee depuis
l'hote, puis referencee par les profils `code-builder`, `codex-builder` et
`qa-agent`.
