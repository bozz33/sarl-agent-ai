# NO-REAL-MONEY-POLICY.md

## Absolute rule
No real order during the demo lab. v1 is backtest/simulation only.

## Block immediately if
- a live account is detected;
- a live tool is requested;
- a live broker credential is provided;
- a real order is requested;
- human validation is absent for a guarded change;
- backtest/simulation mode cannot be proven.

## Required response
```
NO_REAL_MONEY_POLICY_BLOCK:
REASON:
REQUESTED_ACTION:
SAFE_ALTERNATIVE:
```

## Risk disclaimer
This module is a technical learning lab, not financial advice. Trading and day
trading are high risk. FINRA: day trading can lead to the loss of all funds
used. CFTC: verify any forex actor carefully before depositing money or sharing
sensitive information. Any future move toward real money is the user's
responsibility, under strict limits, governance and human validation. See
`SOURCES.md`.
