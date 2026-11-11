# Foundry batch 4: distance-from-extreme filter, 1%-from-open filter, fail-fast exit, exits by day shape (pre-registered)

Written 2026-11-11 15:55 PT by the Researcher (Wednesday build run), **before any result was computed**. Answers BOARD items coach 2026-11-10 (1) and (2), coach 2026-11-09 (1), coach 2026-11-05 (2, the open part) and QUEUE 1a/1b. The sessions that suggested H9/H10 (Oct 28-Nov 10, Nov 5) are inside both archives, so a pass here is weaker than usual and must be confirmed on sessions after Nov 11 before any desk is built from it.

## Data and mechanics (same as batch 3)
- A = 1-min archive `data:backtests/data/etf1m` (Sep 28 to Nov 10), SPY and QQQ, resampled to 5-min. B = 5-min archive `data:backtests/data/etf5m` (Sep 8 to Nov 10).
- Wicks cleaned at ingest (0.4% on 1-min, 0.6% on 5-min). Decide at a 5-min close, fill at the next 5-min open, flat at 15:55. Costs 0.046% round trip (2x stress 0.092%). Day-block bootstrap 95% CI (2,000 draws). Halves = first/second half of each archive's sessions.
- **Random entry set (shared by H9-H11):** each symbol, each day, 3 random 5-min signal bars 09:45-15:05, side random, 8 seeds (so about 24 entries per symbol per day across seeds). Stop 0.5%, otherwise flat at 15:55. Seeds are fixed (21..28) and written in the code before running.
- **Desk set:** floor-lab desk backtest entries `data:backtests/floor/latest/trades_1m.csv` (Oct 1-Nov 10; all longs, including inverse-ETF longs), measured on 1-min bars. Reference index: SPY for SPY/UPRO/SPXU, QQQ for QQQ/TQQQ/SQQQ. For an inverse-ETF long the index side is short.

## H9 distance-from-extreme filter (coach 2026-11-10, LESSONS 33)
- Feature at the signal bar (index, cleaned bars, data up to that bar's close only): long `dist = 1 − close / session high so far`; short `dist = close / session low so far − 1`.
- "Far" = dist ≥ 0.3% (primary). 0.5% and 0.75% are reported as a grid; only 0.3% can pass.
- **Supported** if all of: (a) on random entries, far − near mean net < 0 for longs AND for shorts on both archives (both sides required: one side alone is LESSONS 24's regime); (b) the pooled (both sides) far − near difference has a day-block CI entirely below 0 on at least one archive; (c) same sign in both halves of each archive; (d) on desk entries (index-side mapped), far − near < 0.
- **Refuted** if the pooled far − near difference is ≥ 0 on either archive. Otherwise inconclusive.
- If supported: no desk is built this run (the finding sessions are in-sample); it becomes a forward test on sessions from Nov 12 (paper ledger + foundry), and a `_v2` filter desk is proposed if it holds on 10+ new sessions.

## H10 1%-from-the-open filter (coach 2026-11-05, IDEAS 2026-11-05)
- Feature at the signal bar: long is "stretched" when the index is ≥ 1.0% under the 09:30 open; short when ≥ 1.0% over.
- Count qualifying entries first. If fewer than 20 stretched random entries per archive (per side), it is **untestable** and reported as a count only.
- Otherwise same supported/refuted bar as H9 (stretched − normal), plus the CVD desk entries (cvd_spy, cvd_tqqq) as the desk set.

## H11 fail-fast exit (IDEAS 2026-11-07, LESSONS 30)
- Variant exit added on top of the baseline exit: at the close of the 3rd 5-min bar from the fill (15 minutes), if the best favorable excursion since the fill (long: max high / entry − 1; short: 1 − min low / entry) has never reached +0.10%, exit at that close. Otherwise the baseline exit runs unchanged.
- Applied, paired (same entries, base vs FF), to: random entries (A and B), and the batch 1-3 rule entries re-simulated (F1-F6, ORB2_b10_w1100, PD_HOLD, PD_REJ).
- Desk set on 1-min bars of the traded symbol: if within 15 minutes of the fill the traded symbol's best close-to-high excursion never reached +0.10% x leverage (3 for UPRO/TQQQ/SPXU/SQQQ), exit at the 15th minute's close less spec slippage (0.02% SPY/QQQ, 0.05% 3x); otherwise the desk's own result.
- **Supported** if the paired FF − base mean is > 0 on random entries on both archives, for longs and shorts separately, in both halves, with a CI above 0 on at least one archive, and > 0 on the desk set. **Refuted** if FF − base ≤ 0 pooled on either archive.
- If supported: a new desk key can carry it only for a rule that already has an edge; none does, so it would be a forward test on the paper ledger (count paper trades whose MFE at 15 min was < +0.1%).

## H12 exits by day shape (descriptive; coach 2026-11-09 (1), 2026-11-10 (2))
- Day shape (hindsight label, never an input to a rule), per index per day: **up** close ≥ open + 0.4%; **down** close ≤ open − 0.4%; else **V** if the range ≥ 0.8% of the open, else **chop**.
- Report per cell (n, mean net): F1 (wide cloud exit) vs F2 (tight exit) from batch 1 on both archives, split by side; and for CVD desk entries (1-min): actual CVD exit vs hold to 15:55 vs exit on the first 1-min close below VWAP.
- Pre-stated reading: if the best exit flips with day shape (hold on trend days, tight/CVD on V/chop), there is no usable exit rule unless day shape is knowable at entry, and LESSONS 21 says it was not at 10:30. That would be logged as a lesson, not a desk.

## Variants
H9 3 thresholds + H10 1 + H11 1 + H12 3 exits (descriptive) = 8. Running total 169 → 177.
