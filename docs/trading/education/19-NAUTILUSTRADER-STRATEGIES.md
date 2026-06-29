# 19 — NautilusTrader Strategies

## Structure
Une stratégie hérite de `Strategy`. Elle réagit aux données (ex. `on_bar`),
calcule des indicateurs et soumet des ordres via l'API du moteur.

## Config
Les paramètres passent par une config (msgspec Struct), ex. `EMACrossConfig` :
instrument_id, bar_type, trade_size, fast_ema_period, slow_ema_period.

## v1 module
`eurusd_ema_cross` enveloppe l'exemple officiel `EMACross`. Allow-listée dans
`app/config.py`. Aucune logique live.

## Ajouter une stratégie
Voir `../NAUTILUS-STRATEGY-GUIDE.md` : fichier dans `strategies/`, allow-list,
test smoke, risk review, review. Done = file + test + rapport + diff git.

## Garde-fou
Le scan `guards` rejette tout mot-clé live dans une stratégie.
