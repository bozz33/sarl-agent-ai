# 21 — No Real Money Policy (rappel formation)

## Règle absolue
v1 = backtest/simulation. Aucun ordre réel, aucun broker, aucun argent réel.

## Bloquer immédiatement si
compte live · outil live · credential broker live · ordre réel · validation
humaine absente · mode backtest non prouvé.

## Réponse
```
NO_REAL_MONEY_POLICY_BLOCK:
REASON / REQUESTED_ACTION / SAFE_ALTERNATIVE
```

## Application
Renforcé dans le code (`app/guards.py`, gate de build Docker) et par la skill
`sarl-no-real-money-policy`. Détail : `../NO-REAL-MONEY-POLICY.md`,
`../NO-LIVE-TOOLS.md`.

## Avertissement
Lab technique, pas un conseil financier. Trading à risque élevé. Tout passage
vers le réel = limites strictes, gouvernance, validation humaine (hors v1).
