# Foundry batch 5: results (2026-11-14, Saturday review run)

Pre-registration: `research/foundry/PREREG_batch5.md` (commit b7c1217, before computing). Code `lab/foundry/batch5.py`, tests `lab/tests/test_foundry_batch5.py` (no-look-ahead, next-bar fills). Raw output: `data:backtests/foundry/latest/batch5/` once foundry-lab runs it; this run's copy was computed locally on the same archives.
A = 1-min archive, 35 sessions (Sep 28-Nov 13). B = 5-min archive, 49 sessions (Sep 8-Nov 13). Costs 0.046% round trip. Per-trade numbers in %.

**Verdict: 0 of 4 tests passed. No paper desk added.** H14 profit lock refuted, H15 CVD down-morning gate inconclusive (longs only, the regime pattern), H17 ORB first-break-only refuted (the opposite held). H16 and H18 are descriptions.

## H14 profit-lock exit (arm at +0.7%, exit at the first 5-min close through the 5/12 cloud): refuted
| Set | n | armed | base | lock | paired diff (CI) | long | short | halves |
|---|---|---|---|---|---|---|---|---|
| Random A | 1,680 | 192 | −0.045 | −0.049 | −0.003 [−0.018, +0.010] | +0.004 | −0.011 | −0.003 / −0.004 |
| Random B | 2,352 | 238 | −0.044 | −0.045 | −0.002 [−0.012, +0.011] | 0.000 | −0.004 | −0.002 / −0.001 |
| Floor-lab eod desks (1-min) | 99 | 34 | −0.062 | −0.065 | −0.003 [−0.13, +0.12] | +0.14 | −0.19 | 0.00 / −0.01 |
| H13 cell, A / B | 22 / 25 | 8 / 9 | +0.177 | +0.111 / +0.119 | −0.066 / −0.058 | | | |
- The pre-registered refutation condition holds: the pooled paired diff is ≤ 0 on random entries on both archives. 0.35% and 1.0% arms: −0.008 / −0.009 and −0.001 / +0.001 (reported only).
- By desk it is desk-specific again, as LESSONS 20 found for the giveback trail: orb_vol +0.13 [−0.00, +0.30] (n=22), volspike −0.07 (n=32), ema_vol −0.02, ema_vol_v2 −0.03.
- By day shape (hindsight): the lock helps long trades on chop/V/up days and costs the big winners: desk inverse-ETF longs on down days fall from +2.60 to +1.34 (n=8). This is LESSONS 35 again: the right exit depends on the day's shape, which isn't known at entry.
- It does not help H13 either (−0.06 in both archives), which answers BOARD coach 2026-11-13 (1).

## H15 CVD down-morning gate (QQQ ≤ −0.5% from the open before 10:30; mirror for shorts): inconclusive
Early random entries, every 5-min signal 09:45-10:25, both sides; primary exit 30 minutes (0.5% stop).
| Archive | gated n (days) | pooled gated − other (CI) | long | short | halves |
|---|---|---|---|---|---|
| A | 180 (20) | −0.059 [−0.235, +0.128] | −0.186 (78) | **+0.045** (102) | **+0.022** / −0.110 |
| B | 238 (25) | −0.052 [−0.186, +0.096] | −0.137 (102) | **+0.015** (136) | −0.030 / −0.068 |
- Not refuted (pooled < 0 on both), not supported: the short side doesn't mirror, no CI excludes 0, A's first half has the wrong sign. Buying a down morning is worse; shorting an up morning isn't. One-sided = LESSONS 24's regime until a rising regime says otherwise.
- CVD desk entries: 5 gated of 64 (3 days), −0.64 vs +0.03. Too few to mean anything; LESSONS 39's three stops are 2 of those 5.
- Reported, not testable here: **held to the close**, fighting a 0.5% morning move lost on both sides, in every half of both archives (B: long −0.238, short −0.136; halves −0.19 / −0.19). That is the H10 pattern (LESSONS 36) at a smaller threshold, and it points the same way as H13 (trade with the morning move). It is a lead for a forward test (IDEAS), not a result: it was found here.

## H16 H13 diagnostics (descriptive; H13's forward rule unchanged)
- By fill time: before 11:00 n=10 / 12, mean +0.36 / +0.35 (5 stops each); 11:00-14:05 n=12 / 13, mean +0.03 / +0.02. In-sample, early triggers carried H13. Forward, early triggers lost too: Nov 12 QQQ 10:00 stopped −0.58, Nov 13 QQQ 10:00 −0.07, SPY 10:15 stopped −0.71.
- Stop inactive for the first 15 minutes: +0.026 / +0.023 paired (CI [0.00, +0.08]); it changed one forward trade (Nov 12 QQQ: −0.58 → −0.00).
- **Forward count, re-derived from the archive:** 4 trades from Nov 12, 0 wins, mean −0.484% (5 with Nov 11, −0.498%). The coach's numbers match exactly. 11 to go before the verdict.

## H17 ORB first break only: refuted
- orb_vol entries (floor-lab, Oct 1-Nov 13): first break 9 trades, −0.35%; re-cross 13 trades, −0.055%. The re-crosses were the *less bad* ones, the reverse of the Nov 6 lead (BOARD coach 2026-11-07 (2)).
- orb_plain fires only on the first close above the range by construction (32 of 32 first breaks), so it can't split. No `orb_vol_v2`.

## H18 regime check of LESSONS 24 (batch 1 rules F1-F6, recomputed)
| | A long | A short | B long | B short |
|---|---|---|---|---|
| Before Nov 9 | −0.094 (302) | +0.061 (241) | −0.077 (433) | +0.018 (382) |
| Nov 9-13 (SPY up 4 of 5 days) | **+0.087** (43) | **−0.082** (38) | **+0.063** (42) | **−0.023** (36) |
In the first week with a rising tape, long sides won and short sides lost. The earlier "shorts win" was regime, as 24 said. None of F1-F6 is positive across both regimes.

## Variants
6 counted (H14 x3 arms, H15 x1, H16 delayed stop x1, H17 x1) + 2 reported H15 variants = 8. Running total 178 → 186.
