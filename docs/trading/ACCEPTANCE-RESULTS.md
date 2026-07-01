# ACCEPTANCE-RESULTS.md

Résultats réels du test d'acceptation du module `sarl-module-trading-demo`.
Date : 2026-06-29. Mode : BACKTEST/SIMULATION only. Gemini retiré du trading.
Règle : chaque ligne = artefact vérifié, pas déclaration d'agent.

Mise à jour : 2026-07-01. Le service a évolué depuis la validation initiale :
35 tests verts, 12 tools MCP, IBKR Paper validé en lecture/paper uniquement.

## 1. Tests unitaires
`35 passed` — `/srv/tests` dans le container déployé `sarl-nautilus-runner-mcp`.

## 2. E2E service (CLI)
```
validate-environment : ok, nautilus 1.230.0, paper_only=true, BACKTEST
run-backtest         : produit ordres/positions + PnL, live=false
validate-ibkr        : ok, account_mode=PAPER, gateway=ib-gateway:4004, live=false
artefacts            : summary.json + account/fills/orders/positions_report.csv
journal              : backtests enregistrés, daily_reports générés
```

## 3. Intégration MCP (depuis Hermes)
```
hermes mcp test sarl_nautilus_runner :
  ✓ Connected → http://nautilus-runner-mcp:8200/mcp
  ✓ Tools discovered: 12
    validate-environment, run-backtest, walk-forward, validate-ibkr,
    fetch-ibkr-data, run-sweep, research-iteration, proven-candidates,
    robustness-ladder, generate-report, daily-report, run-mission
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
Ordre réel / broker live      : aucun (interdit)
IBKR Paper read-only          : validé via nautilus-runner
Résilience fallback          : prouvée
```
Hors-scope actuel : délégation auto complète via sarl-orchestrator,
exécution trading paper automatisée, live réel.
