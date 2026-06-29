# ACCEPTANCE-RESULTS.md

Résultats réels du test d'acceptation du module `sarl-module-trading-demo`.
Date : 2026-06-29. Mode : BACKTEST/SIMULATION only. Gemini retiré du trading.
Règle : chaque ligne = artefact vérifié, pas déclaration d'agent.

## 1. Tests unitaires
`22 passed` — `services/nautilus-runner/tests` (dans le container déployé).

## 2. E2E service (CLI)
```
validate-environment : ok, nautilus 1.230.0, paper_only=true, BACKTEST
run-backtest         : 22 ordres, 11 positions, PnL=8443.77, live=false
artefacts            : summary.json + account/fills/orders/positions_report.csv
journal              : backtests enregistrés, daily_reports générés
```

## 3. Intégration MCP (depuis Hermes)
```
hermes mcp test sarl_nautilus_runner :
  ✓ Connected → http://nautilus-runner-mcp:8200/mcp
  ✓ Tools discovered: 5 (validate/run-backtest/generate-report/daily-report/run-mission)
  aucun tool live
```

## 4. Chaîne agentique 4 agents (tous DeepSeek, gemini-free)
| Agent | Modèle | Résultat |
|---|---|---|
| trading-research-agent | deepseek-reasoner | research note + backtest BT-...182751Z (22 ordres, 11 pos, live=false) |
| trading-risk-manager | deepseek-reasoner | RISK_DECISION APPROVED, live_enabled=false, kill_switch=false |
| trading-journal-agent | deepseek-chat | daily report (8 backtests, 0 risk blocks, 0 proposals) |
| trading-qa-agent | deepseek-reasoner | PASS (7 preuves, aucun chemin live) |

Artefacts vérifiés : backtest = 5 fichiers, summary.json live=false ; journal = 8 backtests / 5 daily_reports ; modèles agents = deepseek uniquement.

## 5. Résilience fallback (test déterministe)
Profil clone trading avec primary cassé volontairement (`gemini-DOES-NOT-EXIST-999`,
vérifié avant ET après run) → réponse via fallback `deepseek-reasoner → claude → gpt`,
tool MCP appelé à travers le fallback. → bascule prouvée, y compris au niveau trading.

## 6. Sécurité no-live
Audit grep code exécutable + configs actives : 0 chemin live (seuls matches =
commentaires de garde-fous). Toolsets restreints (computer_use/social/... désactivés).

## Verdict
```
Chaîne trading bout-en-bout : FONCTIONNELLE
Gemini dans le trading       : ZÉRO
Garde-fous no-live           : confirmés
Ordre réel / broker / IBKR   : aucun (interdit)
Résilience fallback          : prouvée
```
Hors-scope v1 : délégation auto via sarl-orchestrator (couche router gemini),
Phase 7 IBKR paper (future + validation humaine).
