# Foundry batch 3: results (2026-11-07, Saturday review run)

Pre-registration: `research/foundry/PREREG_batch3.md`, committed at 0f5466c before any number was computed. Code `lab/foundry/batch3.py`, tests `lab/tests/test_foundry_batch3.py` (no look-ahead: truncating days and changing future bars leave earlier signals unchanged). Raw output: `data:backtests/foundry/2026-11-07/batch3/` (summary.json, trades, random sets, desk overlay).

Data: A = 1-min archive, 30 sessions (Sep 28 to Nov 6). B = 5-min archive, 44 sessions (Sep 8 to Nov 6). SPY + QQQ. Wick cleaning clipped 2 bars on each archive (the Nov 4 10:00 and Nov 5 13:10 SPY bars). Net % per trade on the underlying after 0.046% round trip. CI = day-block bootstrap 95%.

## Bottom line
**0 of 4 candidates passed. No new desk.** Same pattern as batches 1-2: short sides win, long sides lose (LESSON 24). Prior-day break-and-hold loses with a CI below zero on B.

## H5 two-sided opening-range break (ORB2), full grid
| Cell | A n / mean [CI] | B n / mean [CI] | B long / short | B halves | B ex Nov 5-6 | B random p95 |
|---|---|---|---|---|---|---|
| **buf 0.10%, before 11:00 (primary)** | 45 / −0.049 [−0.31, +0.28] | 63 / −0.038 [−0.24, +0.19] | −0.176 / +0.135 | −0.116 / +0.025 | −0.099 | +0.065 |
| buf 0.10%, before 11:30 | 55 / −0.045 | 77 / −0.046 | −0.166 / +0.098 | −0.144 / +0.040 | −0.096 | +0.067 |
| buf 0.10%, until 15:25 | 66 / −0.004 | 95 / −0.016 | −0.140 / +0.127 | −0.115 / +0.073 | −0.055 | +0.045 |
| buf 0.30%, before 11:00 | 19 / −0.009 | 26 / +0.084 | −0.121 / +0.289 | −0.058 / +0.206 | −0.110 | +0.175 |
| buf 0.30%, before 11:30 | 25 / +0.059 | 33 / +0.099 | −0.174 / +0.389 | −0.113 / +0.255 | −0.051 | +0.130 |
| buf 0.30%, until 15:25 | 40 / +0.052 | 55 / +0.050 | −0.144 / +0.252 | −0.117 / +0.189 | −0.039 | +0.072 |
- **Primary fails every condition** (negative on both archives, long side −0.18%, below the random control).
- The 0.30% cells look positive only because of shorts on two days: dropping Nov 5 and Nov 6 turns every cell negative, and every long side is negative. That is the regime (LESSON 24), not a breakout edge. Not adopted, and not a lead.
- **Entry window (BOARD coach 2026-11-07 (2)):** closing the window earlier does **not** help. In the two-sided rule, "until 15:25" beat "before 11:00" on both archives (A −0.004 vs −0.049; B −0.016 vs −0.038). In orb_vol's own floor-lab backtest (19 entries, Oct 1 to Nov 6), entries before 11:00 averaged −0.435% (13) and entries from 11:30 −0.161% (6). No case for an `orb_vol_v2` with an earlier cutoff.
- Why orb_vol bought UPRO at 12:23 on Nov 6: UPRO's opening-range high was 130.78; price chopped around it all morning (121 one-minute closes above it before 12:22). The 12:22 bar closed 131.21 after two closes below, on 10,699 shares (a volume spike), which is a fresh "cross above" under the rule. The rule fires on any re-cross, not only the first break. That is how the spec is written; it is a design weakness, not a bug.

## H6 failed opening drive and continuation
- Drive days (|09:30-09:55 move| ≥ 0.5% SPY / 0.7% QQQ): **2 per symbol in 44 sessions**; at the coach's 0.9% / 1.3%: 1 per symbol. All 4 primary drive days continued to the close (day return had the drive's sign).
- FOD: 2 trades (+0.37%), CONT: 4 trades (+0.82%, one day +2.41% = Nov 5). **Untestable: n far below any bar.** It needs the long history (Alpaca, City Hall `t-alpaca`).
- Extended impulse (|move from the open| ≥ 1.5% within 45 minutes): 1 day on SPY, 2 on QQQ in 44 sessions. Too rare to matter as a filter on this sample.

## H7 prior-day high/low
| Rule | A n / mean [CI] | B n / mean [CI] | B long / short | B halves | B random p95 |
|---|---|---|---|---|---|
| HOLD (break and hold) | 13 / −0.151 [−0.32, +0.02] | 20 / **−0.183 [−0.31, −0.05]** | −0.164 / −0.207 | −0.241 / −0.113 | +0.135 |
| REJ (reject) | 27 / +0.011 [−0.23, +0.34] | 41 / −0.055 [−0.22, +0.16] | −0.103 / −0.010 | −0.159 / +0.034 | +0.054 |
- **HOLD is refuted**: negative on both sides and both halves; the B CI is entirely below zero. A break of yesterday's high or low that holds for two 5-min closes did not follow through in Sep-Nov 2026 (8 of 20 stopped).
- **REJ is refuted**: 20% win rate, below the random control.

## H8 stale-high filter (overlay)
- Random entries: stale vs fresh, by side, on both archives: differences −0.02 to +0.05 points with CIs straddling zero (A long stale −0.0005% vs fresh −0.0019%: stale was slightly *better*).
- Floor-lab desk entries (217): stale −0.005% (38) vs fresh +0.002% (179), diff CI [−0.54, +0.44]. By desk the sign flips (cvd_spy stale worse, cvd_tqqq stale better).
- **Not supported.** The Nov 6 pattern (three longs after a stale high lost) does not generalize on this sample.

## Also computed this run
- **LESSON 23 split by side** (IDEAS 2026-11-04): foundry trades from 13:00 ET, batches 1-2, both archives. Late longs: −0.09 to −0.13% per trade, the same as early longs (−0.09 to −0.12). Late shorts: −0.02 to −0.04%, worse than early shorts (+0.03 to +0.11). So the 13:00 effect is "shorts lose their edge late"; longs are bad at every hour in this regime.
- **Bad-bar check** (BOARD coach 2026-11-05 (1)): cleaning the two SPY wicks changes 4 batch-1 SPY trades on Nov 4 on archive A (F3, F4, F5, F6) and 2 on B (F5, F6); all are losers either way. The Nov 5 13:10 bar changed **no** F1-F4 signal on B (F2's short and its 14:05 stop are unchanged). Post-mortems now clean wicks at ingest (`lab/foundry/postmortem.py`, 0.4% x leverage of the body); Nov 4 and Nov 5 were rebuilt: SPY Nov 4 up-leg 1.108% (was 1.705), down-leg 0.996% (was 1.577); Nov 5 up-leg 1.271% 10:53-11:35 (was 1.397).

## Variants
13 (ORB2 grid 6, FOD 2, CONT 2, HOLD, REJ, stale filter). Running total 156 → 169.
