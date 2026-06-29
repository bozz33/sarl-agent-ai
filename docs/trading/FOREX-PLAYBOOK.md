# FOREX-PLAYBOOK.md

Playbook v1 (backtest). Marché unique au départ : EUR/USD.

## Paires
- v1 : EUR/USD uniquement (liquide, spread faible, macro claire).
- Plus tard : GBP/USD (plus volatil), USD/JPY (sensible aux taux). XAU/USD prudence.

## Sessions
- Londres + New York = liquidité maximale. Asie = souvent range.

## Timeframes
- H1 = contexte / tendance.
- M15 = signal d'entrée.
- M5 = affinement uniquement.

## Indicateurs v1
- EMA 50 / EMA 200 (tendance), RSI 14 (non extrême), ATR 14 (stop).
- Support / résistance, spread, fenêtre news.

## Conditions BUY
tendance H1 haussière · prix > EMA50/200 · pullback propre · RSI non extrême ·
stop basé ATR · RR ≥ 1.5 · pas de news majeure proche.

## Conditions SELL
miroir du BUY (tendance baissière, prix < EMA50/200).

## NO_TRADE
range confus · spread élevé · news proche · signal contradictoire ·
données incomplètes · volatilité anormale · limite journalière atteinte.

## Stratégie v1 implémentée
`eurusd_ema_cross` (EMA cross) via `services/nautilus-runner`. Évolutions :
filtre ATR, règles no-trade, walk-forward, avant tout ajout de marché.
