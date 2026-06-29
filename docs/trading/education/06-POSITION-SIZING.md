# 06 — Position Sizing

## Principe
La taille découle du risque, pas de l'envie. Risque par trade fixé d'avance.

## Formule
```
taille = (capital × risque%) / (distance_stop_pips × valeur_du_pip)
```

## Exemple
Capital 100 000 (virtuel), risque 1 % = 1 000. Stop 25 pips, valeur pip ~10/lot.
-> taille ≈ 1 000 / (25 × 10) = 4 mini-lots (illustratif).

## Règles
- Jamais augmenter la taille pour « se refaire ».
- Réduire la taille si volatilité (ATR) élevée.
- Cohérence avec les limites de perte jour/semaine.

## v1
Le backtest utilise une `trade_size` fixe ; le sizing dynamique viendra avec les
règles de risque enrichies.
