# TRADING-DEMO-LAB.md

Module interne Hermes de SARL-Agent-AI : `sarl-module-trading-demo`.

## Glossaire « live » (éviter toute ambiguïté)
Deux sens distincts — ne pas confondre :
- **« profils Hermes activés »** = les 4 agents trading existent et sont câblés
  au MCP. C'est de l'orchestration interne. ✅ fait.
- **« live trading »** = ordres avec argent réel sur un broker. ❌ INTERDIT en v1.

État sans ambiguïté :
```
Profils Hermes activés : oui
Trading live réel       : non
IBKR Paper read-only    : oui, via nautilus-runner uniquement
IBKR réel/live          : non
NautilusTrader LiveNode / TradingNode : interdit
```
NautilusTrader permet la continuité backtest→live ; c'est précisément pourquoi
la barrière `no-live` (`app/guards.py` + gate de build) reste stricte.

## Objectif
Permettre à Hermes d'apprendre le trading par **backtest/simulation** :
observer, rechercher, proposer une stratégie, lancer un backtest contrôlé,
lire les résultats, journaliser, analyser les erreurs, proposer des
améliorations — sans jamais trader en réel.

## Périmètre v1
- Moteur : NautilusTrader `BacktestEngine` (via `services/nautilus-runner`).
- Marchés allow-listés : EUR/USD, GBP/USD, USD/JPY.
- Stratégies allow-listées : `eurusd_ema_cross`, `eurusd_ema_atr`,
  `donchian_break`, `bollinger_mr`.
- Données : synthétiques déterministes et fetch historique IBKR Paper read-only
  quand la passerelle est disponible.
- Mode : BACKTEST / SIMULATION. Aucun live, aucun ordre réel.
- IBKR Paper : connexion validée en lecture/paper uniquement ; pas d'exécution
  automatique d'ordres paper sans validation humaine explicite.

## Acteurs
```
sarl-orchestrator      coordonne les missions trading
trading-research-agent recherche, hypothèses, stratégie
trading-risk-manager   risque, drawdown, no-trade, blocages
trading-journal-agent  journal, rapports, mémoire
trading-qa-agent       tests, artefacts, diff git, scan no-live
sarl-governor          garde-fous, validation humaine
services/nautilus-runner  barrière de sécurité + exécution backtest
```

## Workflow quotidien (borné, pas de boucle infinie)
```
1. education + sources
2. research note
3. strategy draft
4. risk review
5. backtest (nautilus-runner)
6. reports + journal
7. learning proposal
8. governor review
9. validation humaine si changement de règle
```

## Critères de réussite (30 j)
journal complet · 100 % backtest · 0 live · 0 violation garde-fou ·
rapports présents · règles améliorées avec validation · capacité à dire NO_TRADE.
On juge la discipline et la rigueur, pas seulement le PnL.

## État (2026-07-01)
- Service `nautilus-runner-mcp` : déployé et healthy, image
  `sarl/nautilus-runner:0.12.1`.
- Tests : `35 passed` dans le conteneur déployé (`/srv/tests`).
- MCP : 12 tools allow-listés, dont validation environnement, backtest,
  walk-forward, sweep, rapports, mission bornée, validation/fetch IBKR Paper
  read-only.
- Sécurité : `NAUTILUS_ENVIRONMENT=BACKTEST`, `TRADING_PAPER_ONLY=true`,
  `TRADING_LIVE_ENABLED=false`, pas de `TradingNode`/`LiveNode`.
- IBKR Paper : passerelle connectée et compte paper validé (`DU...`) en
  lecture uniquement. Live réel et ordres réels restent interdits.
- Journal/apprentissage : `journal.db` actif avec backtests, rapports,
  propositions d'apprentissage et candidats de stratégie.
- Qualité stratégie : au moins un candidat marqué `proven` par le journal,
  mais les backtests récents restent mixtes/majoritairement négatifs. Aucune
  stratégie n'est validée pour trading paper automatisé ou production.

## Phase actuelle
```
Phase 1 — Demo/backtest Hermes + Nautilus : fonctionnelle
Phase 1.5 — Orchestration complète via sarl-orchestrator : à durcir
Phase 2 — IBKR Paper : connectivité read-only validée, exécution non autorisée
Phase 3 — Live réel : interdit / hors périmètre
```

Voir `HERMES-TRADING-BOUNDARY.md`, `NO-LIVE-TOOLS.md`, `NAUTILUS-RUNNER-ADAPTER.md`,
`NO-REAL-MONEY-POLICY.md`, `SOURCES.md`.
