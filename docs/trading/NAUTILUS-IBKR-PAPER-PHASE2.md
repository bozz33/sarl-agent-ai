# NAUTILUS-IBKR-PAPER-PHASE2.md

Phase FUTURE uniquement. Pas en v1. IBKR **paper**, jamais live.

## Pré-requis (actions humaines)
- Compte IBKR + paper trading activé.
- Décision data : 15-min delayed gratuit (`reqMarketDataType(3)`) OU temps réel
  forex (~3 $/mois + compte fundé 500 $).
- Credentials IBKR dans `.secrets/` (hors git), 2FA mobile au login (non
  désactivable sur paper depuis fév. 2025).

## Stack
- NautilusTrader extras `ib,docker`.
- IB Gateway **paper** headless via `gnzsnz/ib-gateway-docker` (IBC auto-login).
- TWS ou IB Gateway doit tourner avant connexion ; timestamps en UTC.
- Respecter le pacing : 50 req histo simultanées, 60/10min, 50 msg/s.

## Garde-fous (inchangés)
- `TRADING_LIVE_ENABLED=false` reste. Paper only.
- Aucun `TradingNode` live, aucun ordre réel.
- Activation = validation humaine + revue Governor + tests no-live verts.

## Critère d'entrée en phase 2
backtest local stable · journal OK · risk-manager OK · 30 j d'apprentissage
propre · décision humaine explicite. Voir `MONTH-1-LEARNING-PLAN.md`.
