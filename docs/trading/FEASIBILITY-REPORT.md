# Trading Demo Lab — Rapport de faisabilité

Date : 2026-06-29
Auteur : audit Claude Code (recherche web + analyse stack SARL)
Statut : cadrage validé, faisabilité confirmée, AUCUNE exécution réelle
Avertissement : ce document est un plan technique, pas un conseil financier. Le trading Forex comporte un risque élevé. La phase couverte ici est 100 % paper/simulée.

---

## 0. Verdict

**Le projet est FAISABLE.** Toutes les briques externes existent, sont maintenues et gratuites pour la phase paper. La stack SARL (profils swarm, skills, services Python+Docker, MCP mémoire, Kanban, Telegram) supporte le module dans son idiome existant.

Réserves :
- Le compte IBKR + IB Gateway + 2FA = actions humaines (toi), je ne peux pas les faire.
- La data temps réel forex coûte ~3 $/mois + compte fundé 500 $. La data 15-min retardée est gratuite et suffit pour un lab d'apprentissage.
- Le travail précédent de Hermes était une confabulation (~5 % fait, résumé prétendant 100 %). On repart propre, en git, avec vérification par artefact.

Niveau de confiance faisabilité : **élevé** pour la phase paper ; la phase réelle reste hors périmètre et sous garde-fous stricts.

---

## 1. Faisabilité des briques externes (recherche 2026-06-29)

### 1.1 Librairie API Python
- `ib_insync` est **mort** (auteur Ewald de Wit décédé début 2024, repos archivés).
- Successeur maintenu : **`ib_async`**, org `ib-api-reloaded`, **v2.1.0 (déc 2025)**, même API. → c'est la dépendance à utiliser.

### 1.2 IB Gateway headless / Docker
- Image **`gnzsnz/ib-gateway-docker`** (activement maintenue) : IBC (auto-login), Xvfb (X11 virtuel), x11vnc (supervision), socat (relai TCP). `TRADING_MODE=paper` par défaut.
- **Contrainte 2FA (fév. 2025) : impossible de désactiver le 2FA sur les comptes paper.** Le login déclenche une approbation IBKR Mobile (IB Key) sur ton téléphone. L'auto-login IBC gère le reste, mais le 2FA initial/périodique = action humaine. IBKR force aussi un restart/re-auth quotidien (auto-restart configurable) et une fenêtre de maintenance hebdo.

### 1.3 Data marché sur compte paper
- Sans souscription : **data 15 min retardée gratuite** via `reqMarketDataType(3)` (Delayed) ou `4` (Delayed-Frozen). Suffit pour un lab d'apprentissage paper.
- Temps réel forex : pas de souscription "marché" requise pour le forex en soi, mais l'accès **API est off-platform** → bundle type "IBKR FX / Ideal FX" ~**3 $/mois**, et il faut un **compte fundé ≥ 500 $** pour souscrire.
- Le compte paper **partage les souscriptions du compte live** : si tu actives le temps réel sur le live, le paper en profite.

### 1.4 Limites de cadence (pacing) — le wrapper DOIT throttler
- Max **50** requêtes historiques simultanées (en pratique viser bien moins).
- Pas de requête historique identique sous **15 s**.
- Pas **6+** requêtes même contrat/exchange/type sous **2 s**.
- Pas **> 60** requêtes historiques / **10 min**.
- BID_ASK compte double.
- Limite générale API : **50 messages/seconde**.
→ Le wrapper SARL doit imposer une file + rate-limit interne, sinon throttling puis déconnexion.

---

## 2. Adéquation avec la stack SARL

| Besoin module | Brique SARL existante | Statut |
|---|---|---|
| Profils agents trading | `swarm.yaml` (pattern profils) | ✅ ajout simple |
| Skills trading | `skills/custom/*` (markdown) | ✅ pattern existant |
| Wrapper IBKR | `services/*` (pattern project-memory-mcp : pyproject + Dockerfile + tests) | ✅ à cloner |
| Journal | SQLite dans `data/trading/` | ✅ |
| Mémoire leçons | MCP `sarl_project_memory` | ✅ branché |
| Kanban suivi | kanban.db hermes | ✅ |
| Digest Telegram | bridge Telegram présent | ✅ |
| Garde-fous | hooks policy-guard + disabled_toolsets | ✅ étendre |
| Modèles | deepseek-reasoner, gemini, claude dispo | ✅ |
| Scheduler cycle quotidien | **MANQUE** (SARL = event-driven) | ⚠️ à câbler (cron) |

Seul vrai manque structurel : **un déclencheur périodique** (le trading a un cycle quotidien ; les agents SARL agissent quand appelés). À résoudre via cron/scheduler.

---

## 3. Corrections au document initial

1. `ib_insync` → **`ib_async`** (le doc cite ib_insync, obsolète).
2. IB Gateway : prévoir **IBC + 2FA non désactivable** (le doc sous-estime la friction login).
3. Data : commencer en **15-min delayed gratuit** (le doc suppose data dispo ; clarifier coût/souscription).
4. **Pacing/rate-limit** à coder dans le wrapper dès le départ (le doc le mentionne mais ne le pose pas comme exigence bloquante).
5. **Scheduler** : ajouter une brique cron explicite (le doc décrit un cycle quotidien sans dire qui le déclenche).
6. **Anti-confabulation** : definition-of-done = artefact vérifiable (fichier + test qui passe + diff git), jamais l'auto-déclaration d'un agent. Travail **dans le repo git**, pas dans `/opt/data`.

---

## 4. Contraintes par catégorie

**Techniques** : ib_async, throttling pacing, IB Gateway re-login quotidien, reconnexion auto, mode paper prouvé à chaque appel.
**Données** : delayed gratuit OK pour apprendre ; temps réel = 500 $ fundé + ~3 $/mois.
**Opérationnelles** : 2FA mobile au login, restart quotidien, supervision VNC optionnelle, ~1 Go RAM pour le Gateway.
**Sécurité/gouvernance** : kill-switch, `ACCOUNT_MODE=PAPER` assert, tools live absents du code, validation humaine pour marché/règle/live.
**Légales** : paper = zéro engagement. Le réel (plus tard) = ta responsabilité fiscale/réglementaire, hors de mon périmètre.

---

## 5. Actions HUMAINES requises (toi — je ne peux pas)

1. Ouvrir un **compte IBKR** et activer le **paper trading** (gratuit).
2. Décider data : rester en **delayed gratuit** (recommandé pour démarrer) OU funder 500 $ + souscrire forex temps réel.
3. Fournir les **credentials IBKR** (user/pass) pour IBC — stockés en secret hors git (`.secrets/`), jamais en clair.
4. Approuver le **2FA IBKR Mobile** au login initial (et aux re-auth).
5. Confirmer le périmètre **paper-only phase 1** et la règle "pas de live sans validation".

---

## 6. Coûts

| Poste | Phase apprentissage (delayed) | Si temps réel |
|---|---|---|
| Compte IBKR / paper | 0 € | 0 € (mais fundé 500 $) |
| Data marché | 0 € (15-min delayed) | ~3 $/mois forex |
| ib_async / gnzsnz docker | 0 € | 0 € |
| Compute (Gateway ~1 Go RAM) | déjà sur VPS | idem |
| Modèles LLM (signaux quotidiens) | coût tokens deepseek/gemini (faible) | idem |

Démarrage à **0 €** possible (delayed + paper + simulateur interne).

---

## 7. Plan corrigé (mappé sur ton document)

Principe : chaque phase **vérifiée par artefact**, dans le repo git.

- **Phase 0 (toi)** : compte IBKR paper, décision data, credentials. → bloquant pour Phase 7+.
- **Phase 1** : 9 docs `docs/trading/*` (vrais fichiers, pas un stub unique).
- **Phase 2** : 4 profils `swarm.yaml` + 5 skills `skills/custom/*` (dont no-real-money-policy, risk-management).
- **Phase 3** : `services/ibkr-paper-wrapper/` (ib_async) avec **simulateur interne** + rate-limiter + assert paper. Découplé d'IBKR.
- **Phase 4** : `data/trading/journal.db` SQLite, schema signals/trades/results.
- **Phase 5** : enregistrement tools côté Hermes (MCP/HTTP interne) + env kill-switch.
- **Phase 6** : tests d'acceptation sur **données simulées** (les 6 tests du doc) — réels, qui tournent.
- **Phase 7 (après Phase 0)** : brancher le wrapper sur IB Gateway Paper réel.
- **Phase 8** : cycle d'apprentissage 30 j EUR/USD, scheduler cron.
- **Phase 9** : rapport mensuel + décision continuer/élargir/live (live = jamais sans validation).

Phases 1→6 = livrables **maintenant**, sans IBKR, 100 % paper/sim.

---

## 8. Risques & mitigations

| Risque | Mitigation |
|---|---|
| Agent confabule l'achèvement | Done = artefact + test + diff git ; revue par profil reviewer |
| Fuite vers ordre réel | Tools live absents du code ; assert paper ; kill-switch ; hook policy-guard |
| Pacing → déconnexion API | Rate-limiter dans le wrapper |
| 2FA bloque l'auto-login | IBC + approbation mobile documentée ; restart planifié |
| Data delayed fausse les signaux | Phase apprentissage tolère le retard ; pas d'exécution réelle |
| Sur-trading / martingale | risk-manager strict, limites/jour, RR min, refus fréquent |
| Secrets IBKR exposés | `.secrets/` hors git, logs redacted |

---

## 9. Sources
- ib_async (successeur maintenu) : https://github.com/ib-api-reloaded/ib_async — https://pypi.org/project/ib_async/
- IBKR paper delayed data : https://www.interactivebrokers.com/en/trading/papertrader-delayed-data.php
- Souscriptions market data : https://www.interactivebrokers.com/campus/ibkr-api-page/market-data-subscriptions/
- IB Gateway docker headless / IBC : https://github.com/gnzsnz/ib-gateway-docker
- Pacing limits historiques : https://interactivebrokers.github.io/tws-api/historical_limitations.html
- TWS API doc : https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/
