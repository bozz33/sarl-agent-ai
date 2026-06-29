# 03 — Candlesticks & OHLCV

## Bougie
Représente une période (M5, M15, H1...). Corps = open->close ; mèches = high/low.

## Lecture
- Corps haussier (close > open) vs baissier.
- Mèches longues = rejet de prix / volatilité intrabar.

## OHLCV en pratique
Données minimales d'un backtest : open, high, low, close, volume, horodatées UTC.

## Dans NautilusTrader
Les bougies deviennent des objets `Bar` (via `BarDataWrangler`). Le module v1
fournit des bars BID et ASK pour permettre l'exécution simulée FX.

## Piège
Ne pas confondre source `INTERNAL` (agrégée par le moteur) et `EXTERNAL`
(bougies déjà construites, fournies en données). Le module utilise `EXTERNAL`.
