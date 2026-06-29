# 09 — EMA, RSI, ATR

## EMA (Exponential Moving Average)
Moyenne pondérée vers le récent. EMA 50 / EMA 200 = tendance. Croisement
EMA rapide/lente = signal (base de `eurusd_ema_cross`).

## RSI (Relative Strength Index, 14)
Oscillateur 0-100. > 70 surachat, < 30 survente. Sert de filtre (éviter
d'entrer en zone extrême).

## ATR (Average True Range, 14)
Mesure la volatilité. Sert à placer le stop (ex. stop = k × ATR) et à
dimensionner. ATR élevé = marché plus risqué.

## Usage combiné (v1 cible)
Tendance EMA + entrée sur pullback + RSI non extrême + stop ATR + RR ≥ 1.5.

## Note
v1 implémente le croisement EMA ; RSI/ATR comme filtres viennent ensuite.
