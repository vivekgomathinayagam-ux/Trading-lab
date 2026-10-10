# trading-lab — Compound City

Private repo for Gomes's self-funding trading + side-hustle operation.
Read `STATE.md` first, then `DECISIONS.md`. Every chat and scheduled task does.

## Layout
```
/strategies/<name>/   code, spec.md, config.yaml   (stage: idea→spec→backtest→paper→live_ready→live→retired)
/engine/              config, broker adapters, risk engine, shadow fills, ledger, data push, worker
/backtests/           scripts and results
/ledger/              every order, fill, hustle payment and cost (CSV); pushed to branch "data"
/hustles/<name>/      one-pager, status, work log, revenue
/tests/               unit tests (python -m unittest discover -s tests)
STATE.md              current status
DECISIONS.md          dated log of what changed and why
```

## Running
- Railway worker: `python -m engine.worker` (see railway.toml). Deploys from `main`.
- Connectivity check only: `python -m scripts.check_tradier`
- Tests: `python -m unittest discover -s tests -v`

## Secrets
Only in Railway Variables, typed by Gomes. Names are in `engine/config.py`.
Nothing in this repo holds a token.

## Money rules (summary; full text in the project prompt)
$50 own money total; no margin; no undefined risk; 5% max loss per trade;
10% daily loss stops new live entries; 30% drawdown stops all live trading.
Live orders are impossible until `TRADIER_LIVE_TOKEN` and
`LIVE_TRADING_ENABLED=true` are both set by Gomes.
