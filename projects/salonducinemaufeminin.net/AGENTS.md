# AGENTS.md — salonducinemaufeminin.net

Contexte agent SARL. NE PAS commiter dans le repo projet. Vit côté SARL.

## Projet
- Nom : salonducinemaufeminin.net
- Repo/deploy : `/root/CascadeProjects/salonducinemaufeminin.net`
- Type : **WordPress en PRODUCTION LIVE** (https://salonducinemaufeminin.net)
- Stack : `wordpress:php8.2-apache` + MariaDB 11.4
- Core WP : `./site` (wp-config.php, wp-admin, wp-content…)
- Containers : `salonducinemaufeminin-web`, `-db`, `-cron` (wp-cron toutes 5 min)
- DB : `c1987271c_saalon`. Secrets via `/run/secrets/db_password` (PAS en clair).

## ⚠️ ATTENTION — site en prod
Pas de framework de test JS/Go ici. Validation = WP-CLI + vérif HTTP + visuel.

## Commandes (depuis le dir projet)
- Lint PHP fichier : `php -l <fichier>`
- WP-CLI (dans le container) : `docker compose exec -u www-data web wp <cmd>`
  - ex : `... wp plugin list`, `... wp core verify-checksums`, `... wp db check`
- Logs : `docker compose logs --tail=100 web`
- État : `docker compose ps`
- Backup DB AVANT toute modif DB : `docker compose exec db sh -lc 'mysqldump ...' > backups/...sql`

## Runtimes
php/composer ABSENTS de hermes-agent → travailler via le container WP (`docker compose exec`), pas dans hermes.

## Règles (strictes — prod)
- JAMAIS modifier `wp-config.php`, `.htaccess`, `public_html`, secrets, DNS, SSL sans validation humaine.
- Backup DB + fichiers AVANT tout changement.
- Préférer staging avant prod quand possible.
- Aucune mise à jour plugin/core directe en prod sans validation.
- Checkpoint + rapport systématiques.
