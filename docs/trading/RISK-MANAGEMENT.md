# RISK-MANAGEMENT.md

Règles de risque du module (virtuel, backtest). Appliquées par
`trading-risk-manager` (skill `sarl-trading-risk-management`).

## Limites (v1)
- Risque max par trade : 0.5 % ou 1 % du capital virtuel.
- Perte max / jour : 2 %. Perte max / semaine : 5 %.
- Nombre max de trades / jour : 3 à 5.
- Stop-loss obligatoire. Take-profit obligatoire ou sortie documentée.
- Risk/reward minimum : 1.5R.

## Interdits
- Martingale, moyenne à la baisse, revenge trading.
- Trade sans journal, sans raison explicite, sur données incomplètes.
- Trade pendant news majeure si blackout actif.
- Sur-optimisation / overfitting (validation walk-forward recommandée).

## Position sizing
Taille = (capital × risque%) / (distance stop en pips × valeur du pip).
Jamais d'augmentation automatique de taille.

## Drawdown
Surveiller le drawdown cumulé. Au-delà des limites jour/semaine : NO_TRADE.

## Décision (format imposé)
```
RISK_DECISION:
APPROVED: yes/no
REASON:
BLOCKING_RULE:
MAX_POSITION_SIZE:
STOP_VALID:
RR_VALID:
OVERFIT_RISK:
```

## Avertissement
Lab technique, pas un conseil financier. Le trading Forex est à risque élevé
(FINRA/CFTC, voir `SOURCES.md`). v1 = backtest/simulation, zéro argent réel.
