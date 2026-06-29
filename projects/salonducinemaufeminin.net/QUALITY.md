# QUALITY.md — salonducinemaufeminin.net (WordPress prod)

## Gates obligatoires
- `php -l` sur chaque fichier PHP modifié (lint syntaxe)
- `wp core verify-checksums` (intégrité core WP)
- `wp db check` après changement DB
- Vérif HTTP : page d'accueil + parcours touché répondent 200, pas d'erreur PHP
- QA navigateur (browser tool Hermes) sur le parcours impacté (login, formulaire, page modifiée)
- Review critique (code-reviewer-critical / Claude) car PROD live

## Définition de terminé
- backup pris AVANT modif ;
- `php -l` OK, checksums OK ;
- site répond, pas de fatal PHP dans les logs ;
- parcours utilisateur vérifié ;
- rapport + risques documentés ;
- validation humaine obtenue (prod).

## Interdits sans validation humaine
wp-config.php, .htaccess, secrets, update core/plugin en prod, suppression contenu, migration DB.
