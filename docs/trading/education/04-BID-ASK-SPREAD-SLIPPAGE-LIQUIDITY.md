# 04 — Bid/Ask, Spread, Slippage, Liquidity

## Bid / Ask
- Bid = prix auquel on vend. Ask = prix auquel on achète. Ask > Bid.

## Spread
Ask - Bid. Coût implicite de chaque trade. S'élargit en faible liquidité / news.

## Slippage
Écart entre prix attendu et prix exécuté. Augmente en volatilité / faible liquidité.

## Liquidité
Profondeur du carnet. Forte = exécution propre, faible slippage.

## Conséquence stratégie
- Éviter de trader quand le spread est anormalement élevé (règle NO_TRADE).
- En backtest, modéliser le spread (le module fournit BID + ASK) pour des fills réalistes.

## v1
Spread synthétique fixe dans `app/data.py`. Données réelles plus tard
affineront spread/slippage.
