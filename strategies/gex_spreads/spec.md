# GEX-filtered SPY/SPX vertical spreads
Stage: idea → unblocked 2026-10-26, backtest build queued next.

Vivek's four filters: 0DTE GEX share, IV ratio, pin score, net GEX regime.

Old blocker (stale): GEX source (FlashAlpha; free tier blocks SPY/QQQ/SPX) and historical options quotes (paid) — no honest backtest was possible.

**Unblocked:** Vivek connected Skylit. `heat_historical_heatmap` replays real per-strike dealer gamma/vanna up to 365 days back (SPXW for S&P 0DTE/weekly gamma, not SPX). `option_chain` (per-strike premium/volume/OI by date) and `contract_history` (daily premium, bid/ask execution split, IV per contract over a date range) give real historical options pricing to simulate spread entries/exits. Cost is trivial (≈8 credits/symbol-day) against the connected account's ~$105 balance.

**Still blocking a build:** the four filters' exact definitions are Vivek's own design and aren't written down anywhere in this repo — only named. Needs his thresholds/formulas before coding (asked 2026-10-26); a guessed definition would not be "his design."
- 0DTE GEX share — likely 0DTE gamma as a % of total gamma across all expirations; exact formula/threshold TBD.
- IV ratio — likely short-term IV vs. a longer-dated IV or historical vol; which two, TBD.
- Pin score — likely a measure of how strongly price is pinned to the king node / max-gamma strike; formula TBD.
- Net GEX regime — likely positive vs negative net dealer gamma (long-gamma pinning vs short-gamma trending); exact sign convention and any magnitude threshold TBD.

Once Vivek gives these, data source is Skylit (`heat_historical_heatmap`, `option_chain`, `contract_history`); 365-day history only (not the usual 2+ year gate) — note this as a limit in the report, test walk-forward within that window, and run forward paper for anything beyond it. 365 days also isn't enough to cover more than ~1 full market cycle, so results should be read as preliminary even if they pass the screen.
