# Intraday scalp backtest: pre-registered plan (2026-11-17, approved by Vivek: "go")
Research only. Nothing here trades. Full rules are in the docstring of lab/scalp/backtest.py.
- Tickers (23): SPY QQQ AAPL MSFT NVDA AMZN META GOOGL TSLA AMD (original) + TQQQ SQQQ SOXL UPRO + PFE T CCL SOFI RIOT AAL RIVN F + MARA (stress test, spread above the 10 bps cap).
- Data: Alpaca 1-minute bars (SIP, IEX fallback), regular hours, 2024-11-01 to now. Spreads measured from SIP quotes (8 sessions x 3 times of day).
- Setups (indicators and charts only, no news): orb15, vwap_reclaim, ema_fast_cross, rsi3_fade, vol_spike_mom; long and short.
- Exits: target 0.15-0.75% x stop 0.10-0.30%, time stop 5 minutes. Entry at next bar open; stop first when both hit.
- Metric order: net % (bps) per trade, then $ per trade and per day on $1,000 of whole shares.
- Pass bar on the holdout (2026-05 on), net of costs: mean > 0 with 95% day-block bootstrap CI above 0, PF >= 1.2, >= 200 trades, beats random-entry control, positive on >= 12 of 23 tickers.
- Short side needs margin (money rule 4): shown for information; a live version would be long-only or inverse ETFs.
- Next if something survives: tick-level check on sampled 2026 days, then a paper desk through the Alpaca paper adapter (needs Vivek's yes: broker/order code).
