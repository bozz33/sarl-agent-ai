# Activation sandbox Docker dedie

Non applique.

## Architecture

```text
code-builder / qa-agent
  -> Docker CLI dans hermes-agent
  -> DOCKER_HOST tcp://sandbox-docker:2375
  -> daemon Docker-in-Docker prive
  -> conteneurs sandbox durcis par Hermes
```

Le daemon :

- n'expose aucun port hote ;
- utilise reseau Compose interne ;
- ne monte pas socket Docker hote ;
- ne monte pas `/root`, `.secrets` ou projets ;
- stocke uniquement ses images/volumes dans volume dedie.

## Risque residuel

Le service DinD est `privileged` et partage le noyau hote. Il reduit fortement
le risque compare au montage du socket hote, mais ne constitue pas une VM.
Activation exige validation humaine et test d'evasion/limites.

## Tests requis

1. image `docker:27-dind` epinglee par digest ;
2. aucun port publie ;
3. daemon inaccessible hors reseau interne ;
4. `code-builder` peut lancer commande dans sandbox ;
5. sandbox ne voit ni `/root` ni `.secrets` ;
6. limites CPU/memoire/PID presentes ;
7. `--privileged` interdit aux conteneurs enfants ;
8. cleanup et rollback du volume testes.

## Rollback

Retirer `DOCKER_HOST`, retirer service/reseau/volume Compose, puis supprimer le
volume seulement apres validation destructive distincte.
