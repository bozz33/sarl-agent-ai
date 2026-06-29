# 11 — Backtesting Basics

## Définition
Rejouer une stratégie sur des données historiques pour estimer son comportement.

## Bonnes pratiques
- Données propres, horodatées UTC, sans look-ahead.
- Modéliser spread/commissions/slippage pour du réalisme.
- Mesurer PnL, win rate, profit factor, drawdown max, expectancy.
- Séparer données d'étude et de validation (walk-forward).

## Pièges
- Look-ahead bias (utiliser une info future).
- Survivorship bias, overfitting (voir `12`).
- Conclure sur trop peu de trades.

## Dans le module
`BacktestEngine` (NautilusTrader) via `services/nautilus-runner`. Artefacts :
`summary.json` + rapports CSV. Données synthétiques en v1, réelles ensuite.
