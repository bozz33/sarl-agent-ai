# Real historical data (drop-in)

Put a CSV here named `<dataset>.csv` (columns: timestamp,open,high,low,close,volume).
Run with `--dataset <name>` (or `real` to use the first CSV found) to backtest on
REAL data via the ParquetDataCatalog. Without a CSV, the runner uses a seeded
realistic random walk. No network, no licensing baked in.
