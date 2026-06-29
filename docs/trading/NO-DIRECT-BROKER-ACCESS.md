# NO-DIRECT-BROKER-ACCESS.md

## Policy

```
No Hermes agent receives:
- broker credentials
- a direct broker API
- a live IB Gateway
- a real-order tool
```

## Why
A broker connection is the single most dangerous capability. It is kept out
of every agent's reach. Only `nautilus-runner` could ever hold a (paper-only,
Phase 7+) connection, behind the guards, and never in v1.

## Credentials handling (future paper phase)
- Stored only in `.secrets/` (outside git), never in code, configs, or logs.
- Logs are redacted.
- Injected into the runner container as secrets, never into agent profiles.

## v1
No broker at all. Backtest/simulation only.
