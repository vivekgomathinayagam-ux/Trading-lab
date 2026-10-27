# Research queue (ordered; the Researcher edits this)

_Last set: 2026-10-26 by Claude. Top item first._

## Now
1. **Weekly paper report script** (`lab/floor/paper_report.py`): reads the data-branch ledger and prints the stats in CHARTER "Reading the paper data". Unit-tested on a made-up ledger.
2. **Parity replay** (`lab/floor/replay.py`): replay one date from the archived 1-min bars through the shared core and compare with `ledger/daytrade_trades.csv`. First check: Oct 26 (3 trades).
3. **Split floor-lab**: archive job (stays daily) and replay job. Freeze the Oct 1-23 backtest as the reference.
4. **CVD turn**: pre-register (`strategies/cvd_turn/spec.md`): how 1-min bars approximate volume delta, 3-min aggregation, 5-candle lookback, the spike filter, long-only handling of the "sell" turn (exit, or buy an inverse ETF). Implement as a new rule in `core.py`, backtest once, then paper (Vivek's setup, so paper regardless).
5. **Skylit edge study (the Researcher's own project, top priority after 1-2)**:
   - Map which Skylit tools have history and how far back.
   - Build a cached dataset on branch `data` (`research/skylit/`): GEX boards at fixed decision times (09:45, 10:30, 12:30, 15:00 ET) for SPY/QQQ/SPXW, plus Tempest daily rows.
   - Measure what each feature predicts for the next hours on SPY/QQQ and the 3x ETFs: King-node pull and pins, flip distance, gamma sign vs realized range, wall rejections, IV term structure.
   - Look ahead only at data whose asOf is at or before the decision time.
   - Write findings in the weekly note.
6. **Skylit paper desks**: pre-register 1-3 ETF day-trade setups built from what step 5 found, back-test once, then build `engine/skylit_feed.py` (read-only) and put them on paper.

## Next
7. First pre-registered combos (`research/combos.md`): portfolio of the three paper desks, drop-one, GEX regime as a gate on each day-trade desk. Judged on forward days only.
8. Option spreads from Skylit signals: model-priced first (2x cost stress). Paper needs real-time option prices and an options order path; the order path is `engine/` order code, so it goes to Vivek as one PR plus one City Hall item.
9. New-setup ideas from the CHARTER list, one per week, pre-registered.

## Standing
- Weekly: check the crypto-lab run succeeded (Sat 09:17 UTC); fix lab code if it broke. Pier research only when the Floor queue is empty.
- No open questions for Vivek. The Researcher defines every GEX and Skylit metric itself (Vivek, 2026-10-26).
