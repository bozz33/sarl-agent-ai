# FOREX-PLAYBOOK.md

Playbook v1 (backtest). Départ : EUR/USD. Extension contrôlée : GBP/USD,
USD/JPY.

## Paires
- v1 initial : EUR/USD (liquide, spread faible, macro claire).
- Allow-list actuelle : EUR/USD, GBP/USD, USD/JPY.
- Hors allow-list : XAU/USD et autres marchés tant qu'ils ne sont pas validés.

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
`eurusd_ema_cross`, `eurusd_ema_atr`, `donchian_break`, `bollinger_mr` via
`services/nautilus-runner`. Toute promotion exige walk-forward, robustesse,
journal et validation humaine.
