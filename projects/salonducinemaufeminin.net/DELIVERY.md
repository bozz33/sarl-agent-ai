# DELIVERY.md — salonducinemaufeminin.net (WordPress prod)

## Environnements
- prod (live) — pas de staging permanent connu. Créer staging jetable si changement risqué.

## Déploiement
- AUCUN déploiement/maj auto. Tout passe par validation humaine.
- Changement de fichier = via volume `./site`, container redémarré de façon contrôlée.

## Backup (obligatoire AVANT changement)
- DB : `docker compose exec db sh -lc 'mysqldump -u<user> -p<pass> c1987271c_saalon' > backups/db-AAAAMMJJ.sql`
- Fichiers : copier la zone touchée dans `backups/`.
- Dir `backups/` déjà présent dans le projet.

## Rollback
- Restaurer dump DB + fichiers depuis `backups/`.
- Redémarrer container web.
- Vérifier site répond avant de clore.

## Checklist avant livraison
- backup DB + fichiers OK
- php -l + checksums OK
- site répond 200, logs propres
- parcours QA navigateur OK
- review critique OK
- rollback testé/connu
- validation humaine obtenue
