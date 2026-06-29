# NAUTILUS-STRATEGY-GUIDE.md

Comment ajouter / modifier une stratégie (backtest only).

## Règles
- Toute stratégie vit dans `services/nautilus-runner/strategies/`.
- Elle doit être ajoutée à `ALLOWED_STRATEGIES` (`app/config.py`) pour être exécutable.
- Aucun mot-clé live (`guards.FORBIDDEN_KEYWORDS`) ; le scan échoue sinon.
- Review obligatoire (`code-reviewer`) + risk review (`trading-risk-manager`).

## v1
`eurusd_ema_cross` enveloppe l'exemple officiel `EMACross` :
config = instrument_id, bar_type, trade_size, fast_ema_period, slow_ema_period.

## Ajouter une stratégie
1. Créer `strategies/<nom>.py` (sous-classe `Strategy` Nautilus, aucune logique live).
2. L'allow-lister dans `ALLOWED_STRATEGIES`.
3. Ajouter un test smoke (le backtest tourne + produit des artefacts).
4. Risk review + review. Done = file + test + rapport + diff git.

## Anti-overfitting
Pas d'optimisation aveugle de paramètres sur un seul jeu. Walk-forward attendu
avant toute conclusion de performance.
