# Audit sécurité & santé — 2026-06-24

Audit hors-cron suite aux findings du `sarl-governor` (audit gouvernance du 24 juin).

## CVE

### CVE-2026-48710 — Starlette « BadHost » (Host-header auth bypass) — RÉSOLU
- Réel. Starlette < 1.0.1, bypass d'auth path-based via Host header. Patché en
  Starlette **1.0.1** (21 mai 2026). Affecte FastAPI/Starlette/ASGI.
- **État stack** : Starlette **1.0.1** dans l'image agent (= version patchée) ;
  port `8642` lié à **127.0.0.1** uniquement (pas exposé Internet). **NON vulnérable.**
- Refs : https://nvd.nist.gov/vuln/detail/CVE-2026-48710 · https://badhost.org/

### CVE-2026-10548 — hermes-agent improper authentication (Credential Pool) — APPLICABLE (Medium)
- Réel. NousResearch hermes-agent ≤ **2026.4.23**, fonction
  `_sync_anthropic_entry_from_credentials_file` (`agent/credential_pool.py`).
  Improper authentication, **vecteur LOCAL**, CVSS **5.3 (Medium)**, divulgué 2 juin 2026.
- **État stack** : la fonction est présente dans l'image `0.17.0-ddgs1` → build
  vraisemblablement affecté.
- **Atténuations** : attaque **locale uniquement** (nécessite accès au conteneur/hôte) ;
  accès conteneur restreint ; fichier `~/.claude/.credentials.json` appartient à l'utilisateur `hermes`.
- **Remédiation** : upgrade de l'image `sarl/hermes-agent` vers une version patchée
  (> 2026.4.23 si disponible). = **upgrade stack supervisé** (stack-steward →
  sandbox → tests → validation humaine), pas de mise à jour automatique (risque de casse).
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
- [ ] CVE-2026-10548 : planifier upgrade supervisé de l'image hermes-agent (stack-steward).
- [ ] Optionnel : tuning résilience DeepSeek pour les crons longs.
