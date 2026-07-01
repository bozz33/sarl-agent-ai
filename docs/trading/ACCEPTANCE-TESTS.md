# ACCEPTANCE-TESTS.md

Definition of done = **file + test qui passe + rapport + diff git**. Jamais une
déclaration d'agent (cf. confabulation Hermes du 28 juin : Phases 2-8 prétendues
faites, 0 artefact).

## Suite réelle (`services/nautilus-runner/tests`, 35 tests verts)
- `test_environment.py` — NautilusTrader importable, settings paper par défaut.
- `test_no_live_tools.py` — `LIVE_FORBIDDEN`, mots-clés interdits bloqués,
  `assert_paper_only` échoue closed sur kill-switch / live / env non-backtest.
- `test_backtest_smoke.py` — backtest tourne, positions > 0, artefacts présents,
  `summary.json` cohérent, `live=false`.
- `test_catalog_backtest.py` — backtest depuis catalogue de données.
- `test_strategy_families.py` — familles de stratégies allow-listées.
- `test_strategy_walkforward.py` — walk-forward borné.
- `test_sweep_markets.py` — sweep multi-marchés allow-listés.
- `test_ibkr_check.py` — validation IBKR Paper fail-closed / paper-only.
- `test_viz.py` — génération d'artefacts de visualisation.
- `test_journal_schema.py` — 8 tables créées, écriture backtest + proposal,
  `human_validation_required = 1` par défaut.
- `test_mcp_tools.py` — tools allow-listés, aucun tool live.
- `test_reports_scheduler.py` — digest généré, missions bornées (2 seulement),
  mission inconnue rejetée, cycle quotidien non-live.

## Lancer
```bash
docker build -t sarl/nautilus-runner services/nautilus-runner
docker run --rm --entrypoint python sarl/nautilus-runner -m pytest -q
```
Le build Docker échoue si `test_no_live_tools.py` échoue (gate sécurité).

## Tests d'acceptation fonctionnels (mappés au plan)
1. Paper mode obligatoire -> `assert_paper_only` + `validate-environment`.
2. No live tool -> `test_no_live_tools` + scan keywords.
3. Backtest allow-listé -> `run-backtest` produit summary + reports.
4. Risk rejection -> règles `sarl-trading-risk-management` (risk-manager).
5. Daily report -> `nautilus_daily_report` / mission `daily_trading_demo`.
6. Learning proposal -> `learning_proposals` (human validation requise).
7. IBKR Paper -> `validate-ibkr` vérifie compte paper/read-only, sans ordre.
8. MCP Hermes -> `hermes -p trading-research-agent mcp test sarl_nautilus_runner`
   découvre 12 tools et aucun chemin live.
