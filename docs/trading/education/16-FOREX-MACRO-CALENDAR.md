# 16 — Forex Macro Calendar

## Événements à fort impact
- Taux des banques centrales (FOMC, BCE...).
- Inflation (CPI), emploi (NFP US), PMI, croissance (PIB).
- Discours de banquiers centraux.

## Effet
Le forex bouge fort et vite autour de ces publications. Spread et slippage
augmentent. Risque de gaps.

## Règle module
- Blackout : NO_TRADE autour des news majeures de la paire tradée.
- Le `trading-research-agent` produit une note avec les fenêtres no-trade.

## Format note
```
MARKET_RESEARCH_NOTE:
DATE / MARKET / KEY_EVENTS / MACRO_CONTEXT / NEWS_RISK / NO_TRADE_WINDOWS
```

## Sources
Calendrier économique fiable + données officielles des banques centrales
(voir `../SOURCES.md`). Sans source fiable -> NO_TRADE.
