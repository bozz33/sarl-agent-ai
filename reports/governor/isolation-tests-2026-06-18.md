# Tests isolation et garde-fous - 18 juin 2026

## Hook `sarl-policy-guard`

Tests unitaires : 6/6.

Test natif Hermes sur `docs-scribe` :

```text
docker compose down -> BLOCK
git status --short   -> ALLOW
```

`hermes hooks doctor` :

```text
script executable
allowlist valide
script inchange depuis approbation
smoke test valide
```

Journal runtime actuel :

```text
/opt/data/logs/sarl-policy-guard.log
```

Le montage futur vers `reports/governor/` reste prepare dans le runbook.

## Checkpoints

Profile pilote : `docs-scribe`.

```text
checkpoints.enabled = true
snapshot cree
modification detectee par diff
rollback execute
contenu version-1 restaure
```

Preuve : `CHECKPOINT_ROLLBACK_OK`.

## Worktrees

Helper : `scripts/create-worktree.sh`.

Test :

```text
depot temporaire
branche agent/code-builder-test
worktree code-builder
verification fichier et branche
nettoyage
```

Preuve : `WORKTREE_TEST_OK`.

Dossier projets final :

```text
.gitkeep
```

## Sandbox Docker

Etat :

- Docker hote protege par AppArmor, seccomp et cgroup namespace ;
- CLI Docker presente dans `hermes-agent` ;
- socket Docker hote non monte ;
- image sandbox cible non presente ;
- backend Docker ne peut donc pas etre active actuellement.

Decision securite :

Ne pas monter directement `/var/run/docker.sock` dans Hermes Agent : cela
donnerait un controle quasi-root de l'hote et contredirait le but du sandbox.
Preparer un daemon sandbox dedie/isole avant activation des profils code.
