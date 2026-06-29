# 13 — Walk-Forward Testing

## Idée
Optimiser sur une fenêtre, valider sur la fenêtre suivante (hors échantillon),
puis avancer. Simule l'usage réel d'une stratégie.

## Étapes
1. Découper l'historique en segments (in-sample / out-of-sample).
2. Calibrer sur in-sample.
3. Tester sur out-of-sample (jamais vu).
4. Glisser la fenêtre et répéter.
5. Agréger les performances out-of-sample.

## Pourquoi
C'est la meilleure défense pratique contre l'overfitting : seule la performance
out-of-sample compte vraiment.

## Module
À implémenter au-dessus du `BacktestNode` + données réelles. v1 (synthétique)
sert d'abord à valider le pipeline, pas à conclure sur la performance.
