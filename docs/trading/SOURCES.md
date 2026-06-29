# Trading Demo Lab — Sources officielles

Les décisions techniques NautilusTrader doivent s'appuyer sur la doc officielle.
Les décisions de risque s'appuient sur les règles SARL + sources officielles de risque.

## NautilusTrader
- Documentation : https://nautilustrader.io/docs/latest/
- Installation : https://nautilustrader.io/docs/latest/getting_started/installation/
- Getting Started : https://nautilustrader.io/docs/latest/getting_started/
- Backtesting (concepts) : https://nautilustrader.io/docs/latest/concepts/backtesting/
- Backtest high-level API : https://nautilustrader.io/docs/latest/getting_started/backtest_high_level/
- Concepts : https://nautilustrader.io/docs/latest/concepts/
- Intégration Interactive Brokers : https://nautilustrader.io/docs/latest/integrations/ib/

## Interactive Brokers (phase future paper uniquement)
- TWS API : https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/
- Paper trader delayed data : https://www.interactivebrokers.com/en/trading/papertrader-delayed-data.php
- Souscriptions market data : https://www.interactivebrokers.com/campus/ibkr-api-page/market-data-subscriptions/
- Limites pacing historique : https://interactivebrokers.github.io/tws-api/historical_limitations.html
- IB Gateway headless / IBC (docker) : https://github.com/gnzsnz/ib-gateway-docker

## Librairie Python (phase future)
- ib_async (successeur maintenu de ib_insync) : https://github.com/ib-api-reloaded/ib_async

## Risque / régulation
- CFTC — Forex customer advisory : https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_MustKnowForex.html
- FINRA — Day-Trading Risk Disclosure (Rule 2270) : https://www.finra.org/rules-guidance/rulebooks/finra-rules/2270

## Notes de version (vérifié 2026-06-29)
- NautilusTrader testé : 1.230.0 (Python 3.12, glibc 2.39). Import + backtest OK.
- ib_insync : ABANDONNÉ → utiliser ib_async.
