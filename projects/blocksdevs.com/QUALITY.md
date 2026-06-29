# QUALITY.md — blocksdevs.com

## ⚠️ À compléter
Gates réels inconnus tant que le repo source de `bozz33/blocksdev` n'est pas localisé.
Une fois trouvé, renseigner : test, lint, typecheck, build (probablement npm/pnpm).

## Gates minimaux en attendant
- Container démarre et répond sur `127.0.0.1:8082`
- Pas d'erreur au boot dans `docker compose logs blocksdev`
- Review standard sur tout changement de compose/env

## Définition de terminé (provisoire)
- changement validé sur l'app qui répond ;
- rapport produit ;
- validation humaine si redeploy prod.
