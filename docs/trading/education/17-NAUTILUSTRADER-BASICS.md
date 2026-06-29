# 17 — NautilusTrader Basics

## Quoi
Moteur de trading open source « production-grade », Rust-native, Python, multi-
actifs / multi-venues. Le module l'utilise pour le backtest uniquement.

## Concepts clés
- `Strategy` : la logique (signaux, ordres).
- `BacktestEngine` / `BacktestNode` : exécutent un backtest.
- `Instrument`, `Bar`, `BarType`, venue.
- Reporting : ordres, fills, positions, compte.

## Dans SARL
On ne touche jamais NautilusTrader directement depuis Hermes. On passe par
`services/nautilus-runner` (frontière sécurité). Voir `../HERMES-TRADING-BOUNDARY.md`.

## Versions
Python 3.12-3.14, glibc ≥ 2.35. Testé : 1.230.0. Installation via `uv pip`.

## Interdit v1
`TradingNode`, `LiveNode`, broker, ordre réel.
