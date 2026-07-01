---
name: sarl-module-trading-demo
description: Orchestrer le module Hermes sarl-module-trading-demo en backtest/simulation uniquement avec NautilusTrader via services/nautilus-runner. Impose le workflow education -> recherche -> stratégie -> risque -> backtest -> journal -> rapport, sans jamais trader en réel.
---

# Skill — sarl-module-trading-demo

## Objectif

Permettre à Hermes d'apprendre le trading par backtest/simulation, sans aucun
ordre réel. Hermes orchestre ; NautilusTrader exécute via `services/nautilus-runner`.

## Quand utiliser

Toute mission liée au module Trading Demo Lab : recherche marché, stratégie,
backtest, analyse de résultats, journal, rapport, proposition d'amélioration.

## Principe absolu

Hermes n'appelle jamais NautilusTrader directement et ne parle jamais à un
broker. Hermes demande une action allow-listée à `nautilus-runner`, qui vérifie
les garde-fous puis exécute. Voir `docs/trading/HERMES-TRADING-BOUNDARY.md`.

## Workflow obligatoire

1. Lire `docs/trading/education/` requis + `docs/trading/SOURCES.md`.
2. Produire un `TRADING_RESEARCH_NOTE`.
3. Proposer / ajuster une stratégie allow-listée (review).
4. Faire valider le risque par `trading-risk-manager`.
5. Lancer le backtest via `nautilus-runner` (action allow-listée).
6. Lire les artefacts (summary.json + CSV), écrire le journal.
7. Produire un rapport ; proposer une amélioration si pertinent.
8. Governor review ; validation humaine si changement de règle.

## Interdits

ordre réel · broker direct depuis Hermes · TradingNode/LiveNode · outil live ·
ordre IBKR paper sans validation humaine · modifier une règle de risque sans
validation · déclarer terminé sans artefact.

## Definition of done

file + test qui passe + rapport + diff git. Jamais une simple déclaration.
