> PERSONAL EXPERIMENT (Vivek's request). Not part of the Compound City plan; no decisions depend on it.

# Scalp backtest result (run 2026-11-17, workflow scalp-backtest 44227552089): NO EDGE from indicators/charts alone
Data: Alpaca SIP 1-minute bars, 23 tickers, 512 sessions each (2024-11-01 to 2026-11-17), measured spreads. 480 configs
(5 setups x 2 windows x 2 sides x 6 targets x 4 stops), 5-minute max hold, next-bar-open entry, pessimistic fills.
- Profitable (net of costs) in train: 0 of 480. Validation: 0 of 480. Holdout: 0 of 480. Pre-registered selection found nothing, so the holdout was never used to pick.
- Random-entry control: about -5.5 bps per trade in every split. Best setup cells: -4.4 to -5 bps. Median GROSS edge before any cost: -0.2 bps.
- Cost sensitivity (exploratory, not a gate): with costs cut to the measured spread only (no 0.02% slippage floor), still 0 of 480 profitable in any split.
- By ticker, gross edge before costs is within +/-1 bp for nearly every name (leveraged ETFs SOXL/SQQQ clearly negative). Cheap stocks did not help: their spreads (4-8 bps) cost more than SPY/QQQ (<1 bp).
- Result only: 1-minute momentum, breakout, VWAP, EMA and RSI signals on these tickers carry no measurable edge at a 0.15-0.75% target.
Files on branch data: backtests/scalp/RESULTS.md, grid_pooled.csv, grid_by_ticker.csv.gz.
