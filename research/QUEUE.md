# Research queue (ordered; the Researcher edits this)

_Last set: 2026-10-26 by Claude. Top item first._

## Now
1. **Weekly paper report script** (`lab/floor/paper_report.py`): reads the data-branch ledger and prints the stats in CHARTER "Reading the paper data". Unit-tested on a made-up ledger.
2. **Parity replay** (`lab/floor/replay.py`): replay one date from the archived 1-min bars through the shared core and compare with `ledger/daytrade_trades.csv`. First check: Oct 26 (3 trades).
3. **Split floor-lab**: archive job (stays daily) and replay job. Freeze the Oct 1-23 backtest as the reference.
4. **CVD turn**: pre-register (`strategies/cvd_turn/spec.md`): how 1-min bars approximate volume delta, 3-min aggregation, 5-candle lookback, the spike filter, long-only handling of the "sell" turn (exit, or buy an inverse ETF). Implement as a new rule in `core.py`, backtest once, then paper (Vivek's setup, so paper regardless).
5. **GEX Stage A**: with the assumed definitions in `strategies/gex_spreads/spec.md` (clearly labeled as Claude's), reconstruct daily GEX labels for the last 365 days from `heat_historical_heatmap` (asOf at or before the decision time) and Tempest rows. Measure what the regime predicts: next-hours realized range and direction on SPY/QQQ. Budget: within the weekly Skylit cap.

## Next
6. First pre-registered combos (`research/combos.md`): portfolio of the three paper desks, drop-one, GEX regime as a gate on each day-trade desk. Judged on forward days only.
7. GEX Stage B: model-priced SPY verticals (2x cost stress). Stage C (paper) needs real-time option prices: the bot already has `SKYLIT_API_KEY` (added Oct 26; read-only key used for price checks) and may need `engine/` work, which goes to Vivek as one PR and one City Hall item.
8. New-setup ideas from the CHARTER list, one per week, pre-registered.

## Standing
- Weekly: check the crypto-lab run succeeded (Sat 09:17 UTC); fix lab code if it broke. Pier research only when the Floor queue is empty.
- Open questions for Vivek (GEX spec section 7) stay open and do not block anything. Proceed on the labeled assumptions.
