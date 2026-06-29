# NAUTILUS-STRATEGY-GUIDE.md

Comment ajouter / modifier une stratégie (backtest only).

## Règles
- Toute stratégie vit dans `services/nautilus-runner/strategies/`.
- Elle doit être ajoutée à `ALLOWED_STRATEGIES` (`app/config.py`) pour être exécutable.
- Aucun mot-clé live (`guards.FORBIDDEN_KEYWORDS`) ; le scan échoue sinon.
- Review obligatoire (`code-reviewer`) + risk review (`trading-risk-manager`).

## Stratégies allow-listées (`app/config.py` STRATEGY_SPECS)
- `eurusd_ema_cross` — exemple officiel `EMACross` (croisement EMA nu).
- `eurusd_ema_atr` — **enrichie** : EMA (tendance) + RSI (filtre extrêmes) + ATR
  (no-trade si volatilité extrême + stop/target ATR). Réduit le surtrading et
  monte le win rate vs le cross nu (vérifié : 216 vs 450 ordres, 36% vs 25% WR).

## Walk-forward (anti-overfitting)
`app/walk_forward.py` : découpe les données en folds out-of-sample séquentiels,
backteste la stratégie (paramètres fixes) sur chacun, agrège (mean PnL, stdev,
win rate moyen, folds profitables, `consistent`). Une stratégie qui ne marche
que sur une période s'effondre ici. CLI `walk-forward`, MCP `nautilus_walk_forward`.

## Ajouter une stratégie
1. Créer `strategies/<nom>.py` (sous-classe `Strategy` Nautilus, aucune logique live).
2. L'allow-lister dans `ALLOWED_STRATEGIES`.
3. Ajouter un test smoke (le backtest tourne + produit des artefacts).
4. Risk review + review. Done = file + test + rapport + diff git.

## Anti-overfitting
Pas d'optimisation aveugle de paramètres sur un seul jeu. Walk-forward attendu
avant toute conclusion de performance.
