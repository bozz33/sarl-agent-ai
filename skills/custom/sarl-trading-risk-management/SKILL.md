---
name: sarl-trading-risk-management
description: Imposer la discipline de risque du module trading (backtest). Le trading-risk-manager valide ou bloque une stratégie/backtest selon drawdown, risk/reward, anti-martingale, anti-overfitting, et refuse souvent. Aucune règle de risque modifiée sans validation humaine.
---

# Skill — sarl-trading-risk-management

## Objectif

Empêcher les stratégies/backtests incohérents ou trop risqués. Le risk-manager
est strict, conservateur et refuse souvent.

## Quand utiliser

Avant tout backtest validé, et pour réviser une stratégie ou une proposition.

## Règles minimales (v1, virtuel)

- risque max par trade : 0.5 % ou 1 %
- perte max / jour : 2 % · / semaine : 5 %
- stop-loss et take-profit obligatoires (ou sortie documentée)
- risk/reward minimum : 1.5R
- pas de martingale, pas de moyenne à la baisse
- pas de stratégie sans journal
- overfitting / sur-optimisation signalés et bloqués
- walk-forward recommandé avant toute conclusion

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

## Interdit sans validation humaine

modifier une règle de risque · augmenter le risque · ajouter un marché ·
activer un quelconque chemin live.
