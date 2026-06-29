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
IBKR réel               : non
NautilusTrader LiveNode / TradingNode : interdit v1
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
- Marché : EUR/USD uniquement.
- Stratégie : EMA cross (`eurusd_ema_cross`).
- Données : synthétiques déterministes (réelles via ParquetDataCatalog plus tard).
- Mode : BACKTEST / SIMULATION. Aucun live, aucun broker, aucun ordre réel.

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

## État (2026-06-29)
- Service `nautilus-runner` : implémenté, backtest EUR/USD EMA-cross qui tourne,
  14 tests verts, image `sarl/nautilus-runner:0.1.0` (build gate no-live OK).
- Docs sécurité : boundary / no-live / no-broker / no-real-money / adapter / sources.
- À faire : corpus education, profils swarm, skills, journal.db, scheduler, rapports.

Voir `HERMES-TRADING-BOUNDARY.md`, `NO-LIVE-TOOLS.md`, `NAUTILUS-RUNNER-ADAPTER.md`,
`NO-REAL-MONEY-POLICY.md`, `SOURCES.md`.
