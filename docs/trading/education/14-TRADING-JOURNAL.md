# 14 — Trading Journal

## Pourquoi
Sans journal, pas d'apprentissage. Chaque décision tracée devient une leçon.

## Contenu d'une entrée
date · marché · timeframe · direction · raison · contexte · news · volatilité ·
entrée · stop · take-profit · taille · résultat · erreur · leçon.

## Discipline
- Écrire AVANT et APRÈS (hypothèse puis résultat).
- Ne jamais supprimer le journal.
- Distinguer erreur de process (mauvaise discipline) et variance (malchance).

## Module
SQLite `journal.db` (`app/journal.py`), tables signals/backtests/.../learning_proposals.
Le `trading-journal-agent` écrit et résume ; leçons importantes -> mémoire MCP.
Schéma : `../TRADING-JOURNAL-SCHEMA.md`.
