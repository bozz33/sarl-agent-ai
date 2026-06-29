# 12 — Overfitting & Bias

## Overfitting
Ajuster une stratégie au bruit du passé. Elle brille en backtest et échoue en réel.

## Signes
- Trop de paramètres optimisés.
- Performance qui s'effondre hors échantillon.
- Résultats trop beaux (win rate ~100 % sur données réelles = suspect).

## Biais fréquents
- Look-ahead : utiliser une donnée future.
- Survivorship : ignorer les actifs disparus.
- Data snooping : tester mille variantes et garder la meilleure par chance.

## Défense
- Walk-forward (`13`).
- Peu de paramètres, logique simple et robuste.
- Validation hors échantillon avant toute conclusion.

## Règle module
Le `trading-risk-manager` signale et bloque la sur-optimisation. Une win rate
parfaite sur données synthétiques n'est PAS une preuve (cas v1 attendu).
