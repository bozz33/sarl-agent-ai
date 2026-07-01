# NAUTILUS-IBKR-PAPER-PHASE2.md

Phase 2 partielle. IBKR **paper**, jamais live.

État 2026-07-01 :
- Passerelle `ib-gateway` lancée sous profil `ibkr`.
- `nautilus-runner` joint `ib-gateway:4004`.
- `validate-ibkr` confirme un compte paper (`DU...`) et `live=false`.
- Usage autorisé : validation et récupération de données historiques read-only.
- Usage non autorisé : ordre paper automatisé, ordre réel, live trading.

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

## Critère avant exécution paper automatisée
backtests robustes · journal OK · risk-manager OK · 30 j d'apprentissage
propre · stratégie approuvée · décision humaine explicite. Voir
`MONTH-1-LEARNING-PLAN.md`.
