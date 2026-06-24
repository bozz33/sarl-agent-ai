# Audit sécurité & santé — 2026-06-24

Audit hors-cron suite aux findings du `sarl-governor` (audit gouvernance du 24 juin).

## CVE

### CVE-2026-48710 — Starlette « BadHost » (Host-header auth bypass) — RÉSOLU
- Réel. Starlette < 1.0.1, bypass d'auth path-based via Host header. Patché en
  Starlette **1.0.1** (21 mai 2026). Affecte FastAPI/Starlette/ASGI.
- **État stack** : Starlette **1.0.1** dans l'image agent (= version patchée) ;
  port `8642` lié à **127.0.0.1** uniquement (pas exposé Internet). **NON vulnérable.**
- Refs : https://nvd.nist.gov/vuln/detail/CVE-2026-48710 · https://badhost.org/

### CVE-2026-10548 — hermes-agent improper authentication (Credential Pool) — RÉSOLU (déjà patché)
- Réel. NousResearch hermes-agent ≤ **2026.4.23**, fonction
  `_sync_anthropic_entry_from_credentials_file` (`agent/credential_pool.py`).
  Improper authentication, **vecteur LOCAL**, CVSS **5.3 (Medium)**, divulgué 2 juin 2026.
- **État stack** (investigation stack-steward + confirmation) : version réelle
  `Hermes Agent v0.17.0 (2026.6.19) · upstream 2bd1977d`. Mapping versions :
  v0.11.0 = 2026.4.23 (affectée) ; v0.17.0 = **2026.6.19** (3+ releases après le
  seuil CVE de 2026.4.23). La fonction existe toujours mais dans sa forme **corrigée**
  (présence ≠ vulnérabilité). **NON vulnérable** — aucun upgrade nécessaire.
- Atténuation résiduelle : vecteur local uniquement de toute façon.
- Refs : https://nvd.nist.gov/vuln/detail/CVE-2026-10548 · https://cvefeed.io/vuln/detail/CVE-2026-10548

## Santé Workspace & stack (2026-06-24)

- Conteneurs : `sarl-hermes-agent` (healthy), `sarl-hermes-workspace` (healthy),
  `sarl-project-memory-mcp` (healthy), `sarl-sandbox-docker` (up).
- Ressources : CPU < 3 %, mémoire < 1 % (47 Gio dispo). Disque hôte VPS : **17 %** (79G/484G).
- Workspace : port `127.0.0.1:3000`, HTTP 200, latence **~9 ms**. **Zéro erreur** logs 24 h.
- Connectivité Workspace → gateway agent (`:8642`) : OK (réponse HTTP).
- Point d'attention mineur : DeepSeek « stream stale 180s / Broken pipe » sur longs
  appels cron (instabilité **API externe**, auto-récupérée par retry). Piste : augmenter
  le seuil de stale ou préférer un modèle plus stable pour les jobs longs.

## Actions
- [x] CVE-2026-48710 : vérifié patché (Starlette 1.0.1) + port localhost.
- [x] CVE-2026-10548 : vérifié — version 0.17.0 (2026.6.19) au-dessus du seuil
  2026.4.23, déjà patché. Aucun upgrade requis.
- [ ] Optionnel : tuning résilience DeepSeek pour les crons longs.

## Note process
L'investigation supervisée (tâche Kanban → stack-steward, deepseek) a produit une
analyse correcte mais a épuisé son budget d'itérations (`max_turns: 10`) avant
d'écrire le fichier de proposition. Correctif appliqué : `max_turns` relevé pour
`sarl-stack-steward` + création du dossier `improvement-proposals/` du profil.
