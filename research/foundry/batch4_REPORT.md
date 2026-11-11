# Foundry batch 4 report (2026-11-11, Wednesday build run)

Pre-registration: `research/foundry/PREREG_batch4.md` (commit 0fd45b8, before computing; amendment 1 for H13, commit ab4b838, before H13 was computed). Code `lab/foundry/batch4.py`, tests `lab/tests/test_foundry_batch4.py` (no look-ahead, next-bar fills, costs). Raw numbers `research/foundry/batch4_summary.json`; foundry-lab now runs batch 4 every weekday (`data:backtests/foundry/latest/batch4/`).

Data: A = 1-min archive, 32 sessions (Sep 28-Nov 10), SPY+QQQ; B = 5-min archive, 46 sessions (Sep 8-Nov 10). 2 / 3 bad wicks clipped. Random set: 3 entries per symbol per day x 8 seeds, both sides, 0.5% stop, flat 15:55 (A 1,536 entries, B 2,208; mean −0.045% / −0.041% per trade, the cost). Desk set: 230 floor-lab desk backtest entries (Oct 1-Nov 10) on 1-min bars. All numbers % per trade after 0.046% round-trip cost; CIs are day-block bootstrap 95%.

**Bottom line: 0 of 4 pre-registered tests passed; the amendment rule (H13) failed 2 of 7 conditions. No new desk, no retirement.**

## H9 distance from the session extreme (coach 2026-11-10, LESSONS 33): refuted
| Archive, 0.3% (primary) | far n | far | near | far − near | CI |
|---|---|---|---|---|---|
| A pooled | 813 | −0.053 | −0.036 | −0.017 | [−0.15, +0.10] |
| A long / short | 407 / 406 | −0.109 / +0.003 | −0.092 / +0.021 | −0.017 / −0.018 | |
| B pooled | 1,148 | −0.036 | −0.048 | **+0.012** | [−0.07, +0.09] |
| B long / short | 551 / 597 | −0.089 / +0.013 | −0.072 / −0.019 | −0.017 / **+0.032** | |
- Pre-registered refutation: pooled far − near ≥ 0 on B. Halves disagree on both archives (A +0.018 / −0.045; B +0.045 / −0.023).
- Grid: at 0.75% far longs are worse on both archives (−0.065 A, −0.095 B; CIs include 0), but far shorts are not (−0.052 A, +0.029 B). A long-only effect is LESSONS 24's down-drift regime, not a filter.
- Desk entries (index side mapped): far −0.148 (49) vs near +0.054 (181), diff −0.20, CI [−0.75, +0.32], halves +0.26 / −0.53. Not decisive either way.

## H10 1%-from-the-open (coach 2026-11-05): inconclusive (too few days)
- Stretched random entries: A 69 long + 31 short on 10 distinct days; B 66 + 50 on 14 days. Desk entries: 5, all on Nov 5 (so the CVD-desk version is untestable: 1 day).
- Stretched − normal: A −0.177 [−0.31, +0.18], B −0.140 [−0.28, +0.07]; both sides negative on both archives; halves A −0.155/−0.181, B −0.005/−0.186. Every sign agrees, but neither CI excludes 0 → inconclusive by the pre-registered bar.
- Read: buying 1% under the open and shorting 1% over it both lose. That is the mirror of trading *with* a 1% move, which led to H13.

## H11 fail-fast exit (exit at 15 min if never +0.10%): refuted
| Set | n | triggered | FF − base | CI | long / short |
|---|---|---|---|---|---|
| Random A | 1,536 | 975 | +0.000 | [−0.012, +0.012] | +0.027 / −0.027 |
| Random B | 2,208 | 1,484 | +0.002 | [−0.008, +0.012] | +0.019 / −0.016 |
| Batch 1-3 rule entries A | 668 | 228 | **−0.001** | [−0.026, +0.020] | |
| Batch 1-3 rule entries B | 974 | 382 | +0.003 | [−0.016, +0.017] | |
| Desk entries (1-min, 15 min, 0.1% x leverage) | 230 | 134 | **−0.064** | [−0.27, +0.11] | |
- No effect on random or rule entries, opposite signs by side, and worse on the desks (volspike −0.08, volspike_2x −0.15, orb_vol −0.09; only cvd_spy +0.06 with n=29). Slow starters are not reliably losers. This also answers LESSONS 30: the entries that never go green are not identifiable at 15 minutes.

## H12 exits by day shape (descriptive; coach 2026-11-09 (1), 2026-11-10 (2))
Day shape is a hindsight label: up ≥ +0.4% open→close, down ≤ −0.4%, V = range ≥ 0.8% otherwise, chop = the rest (A: 14 up / 15 down / 16 V / 19 chop symbol-days; B: 20 / 21 / 19 / 32).

F1 (wide cloud exit) vs F2 (tight exit), mean net % (n), B archive (A agrees in every cell's ranking):
| Side, day | F1 | F2 | better |
|---|---|---|---|
| Long, up | +0.14 (24) | +0.03 (40) | F1 |
| Long, down | −0.19 (11) | −0.03 (14) | F2 |
| Long, V | −0.23 (34) | −0.16 (31) | F2 |
| Long, chop | −0.08 (43) | −0.05 (54) | F2 |
| Short, down | +0.59 (25) | +0.20 (48) | F1 |
| Short, up | −0.26 (14) | −0.11 (18) | F2 |
| Short, V | −0.09 (16) | −0.05 (26) | F2 |
| Short, chop | −0.11 (30) | −0.10 (42) | ≈ |

CVD desk entries (1-min, floor-lab backtest): actual CVD exit vs hold to 15:55 vs first close below VWAP, mean % (n):
| Desk, day | CVD exit | hold | VWAP exit |
|---|---|---|---|
| cvd_tqqq up (9) | +0.55 | **+1.61** | +0.26 |
| cvd_tqqq down (8) | **−0.24** | −4.04 | −0.20 |
| cvd_tqqq V (10) | **+0.26** | −0.17 | −0.29 |
| cvd_spy up (5) | +0.22 | **+0.40** | +0.14 |
| cvd_spy down (5) | −0.57 | −1.27 | **−0.04** |
| cvd_spy chop (13) | −0.06 | **+0.07** | −0.08 |
- The wide exit / hold wins only on days that trend the trade's way; the tight / CVD exit wins everywhere else. As pre-stated, that is not a rule unless day shape is known at entry, and LESSONS 21 says it was not at 10:30.
- Across all days cvd_tqqq's CVD exit (+0.20%/trade, 29) beats holding (about −0.66%): the early sell that cost the Nov 9 leg is the insurance that saved Nov 5 and Nov 10. Keep it.

## H13 1%-from-the-open continuation (amendment 1): fails the bar
Signal: the first 5-min close 09:45-14:00 at ≥ 1% from the 09:30 open, trade with it, stop at the open/entry midpoint, flat 15:55.
| | A (1-min) | B (5-min) |
|---|---|---|
| Trades (days) | 17 (13) | 20 (16) |
| Mean net | +0.375 | +0.346 |
| CI | [−0.17, +1.03] | [−0.12, +0.90] |
| Halves | +0.15 / +0.50 | **−0.05** / +0.48 |
| Long / short | +0.02 (6) / +0.57 (11) | +0.11 (8) / +0.51 (12) |
| 2x costs | +0.33 | +0.30 |
| Without Nov 5-6 | +0.07 | +0.09 |
| Random control p95 | 0.25 | 0.16 |
- Fails: A's CI lower bound (−0.17 vs > −0.02 required) and B's first half (−0.05). Passes the other five.
- Most of the mean is Nov 5 (SPY and QQQ shorts +2.6% each). Without Nov 5-6 it is +0.07 to +0.09% per trade on 15-18 trades: thin.
- It was suggested by these same archives, so even a pass would only have earned a forward test. Kept as a forward lead: foundry-lab now logs it every session; judge on sessions from Nov 12 only (wrong if the first 15 new trades average ≤ 0). First unseen session (Nov 11, not in the computed archives, before the official Nov 12 start): QQQ long 12:25 stopped at −0.55%. (foundry-lab run 2026-11-11 23:54 UTC, 5-min archive now through Nov 11.)

## Board answers
- coach 11-09 (2): Nov 5 cvd_tqqq paper 10:09 was a late fill of the lab's 09:54 signal (the stale-skip bug, LESSONS 31, PR #3). Nov 9 10:09 was a real 10:09 signal (lab 10:09 too). Nov 10 matched (10:21).

## Variants
H9 3 + H10 1 + H11 1 + H12 3 + H13 1 = 9. Running total 169 → 178.
