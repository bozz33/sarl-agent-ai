---
name: sarl-no-real-money-policy
description: Politique absolue du module trading — aucun ordre réel, aucun broker live, aucun outil live, aucun credential live. Bloque immédiatement et notifie le Governor à la moindre tentative de chemin réel. Backtest/simulation uniquement.
---

# Skill — sarl-no-real-money-policy

## Règle absolue

Aucun ordre réel pendant le demo lab. v1 = backtest/simulation uniquement.

## Quand utiliser

En permanence, dans toute mission du module trading.

## Bloquer immédiatement si

compte live détecté · outil live demandé · credential broker live fourni ·
ordre réel demandé · validation humaine absente pour un changement gardé ·
mode backtest/simulation non prouvé.

## Réponse imposée

```
NO_REAL_MONEY_POLICY_BLOCK:
REASON:
REQUESTED_ACTION:
SAFE_ALTERNATIVE:
```

## Application technique

Renforcé dans le code par `services/nautilus-runner/app/guards.py`
(`assert_paper_only`, scan des mots-clés interdits) et par le gate de build
Docker. Voir `docs/trading/NO-LIVE-TOOLS.md` et `NO-REAL-MONEY-POLICY.md`.

## Avertissement

Lab technique, pas un conseil financier. Tout passage vers le réel = limites
strictes, gouvernance et validation humaine (hors v1).
