# Foundry batch 6: results (Researcher, Wed 2026-11-18)

Pre-registration: `PREREG_batch6.md` (commit 1425cd8, before any number below). Code: `lab/foundry/batch6.py`, `lab/foundry/skylit6.py`, tests `lab/tests/test_foundry_batch6.py`. Raw output: `data:backtests/foundry/batch6/`.
**Verdict: 0 of 6 hypotheses passed. No new desk.** The long archive (1,729 sessions, 2020-2026) ends the two open forward tests and the 13:00 cutoff.

All figures are % per trade after 0.046% round-trip costs; CI = day-block bootstrap 95%. L1/L2 = first/second half of the long archive.

## H19: H13 (trade with a 1% move from the open, midpoint stop) on the long archive — REFUTED
| | n | mean | CI | L1 | L2 | 2026 | long | short | 2x cost | rand p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| L (2020-26) | 1,114 | +0.002 | [−0.053, +0.061] | +0.002 | +0.002 | +0.033 (117) | −0.001 | +0.004 | −0.044 | −0.013 |
| A (1-min, 37 sess.) | 26 | +0.149 | [−0.25, +0.62] | | | | −0.18 | +0.32 | | |
| B (5-min, 51 sess.) | 29 | +0.152 | [−0.20, +0.58] | | | | −0.08 | +0.29 | | |
The short archives where it was found still look positive, and only through shorts (the Sep-Nov down-drift, LESSONS 24). Over six years it is zero before costs at 2x. Forward record (1 win in 8 since Nov 12) agrees. LESSONS 36 refuted; the forward test is closed.

## H20: trade with a 0.5% morning move (09:45-10:25), hold to the close — FAILS
| variant | n | mean | CI | L1 | L2 | long | short | 2x |
|---|---|---|---|---|---|---|---|---|
| no stop (primary) | 1,427 | +0.026 | [−0.056, +0.107] | −0.009 | +0.077 | +0.077 | −0.023 | −0.020 |
| 0.5% stop | 1,427 | +0.019 | [−0.028, +0.071] | +0.024 | +0.012 | +0.015 | +0.022 | −0.027 |
| fade (opposite side) | 1,427 | −0.118 | [−0.199, −0.036] | −0.083 | −0.169 | | | |
The continuation is about +0.07% gross: smaller than the round trip's 0.046% x 2. The fade loses with the CI below 0 in both halves, so the half of LESSONS 42 that says "don't fight a 0.5% morning move" holds on 6 years; the "trade with it" half has no edge after costs. The long side's +0.077 is SPY/QQQ's upward drift since 2020, not the signal. Forward test closed.

## H21: no new entries from 13:00 — REFUTED as a rule
Random entries (82,992 trades, 0.5% stop, flat at the close), late (signal ≥ 13:00) minus early:
- longs −0.012 [−0.032, +0.005] (L1 −0.013, L2 −0.012); shorts +0.007 [−0.013, +0.026] (L1 0.000, L2 +0.013).
Late longs are a hair worse, late shorts no worse. The CI includes 0 for both sides, so the pre-registered rule is refuted: there is no 13:00 effect in six years of SPY/QQQ. The paper count (every paper entry from 13:00 lost, 5 independent trades) stays a description of these desks in this regime. LESSONS 23 struck.

## H22: first-hour range vs its 20-day mean as a day-type marker at 10:30 — REFUTED
Trade the first hour's direction at 10:30, 0.5% stop, hold to close:
| gate | n | mean | CI | L1 | L2 | 2026 | long | short |
|---|---|---|---|---|---|---|---|---|
| R ≥ 1.25 | 828 | −0.002 | [−0.06, +0.06] | +0.038 | −0.039 | −0.105 | −0.035 | +0.024 |
| R ≥ 1.5 (primary) | 473 | +0.023 | [−0.07, +0.12] | +0.103 | −0.060 | −0.147 | −0.013 | +0.047 |
| R ≥ 2.0 | 177 | +0.012 | [−0.15, +0.18] | +0.106 | −0.099 | −0.075 | −0.015 | +0.029 |
It worked in 2020-2022 and stopped. Paired exit comparison on the same gated entries: hold +0.023 vs the tight 5/12-EMA exit −0.023 (R ≥ 1.5), +0.012 vs +0.026 (R ≥ 2): no exit choice is reliably better on "big first hour" days either. LESSONS 21 now holds on 6 years: the day's type is not known at 10:30 from the first hour's size.

## H23: Skylit market tide (daily net premium) — REFUTED
358 days (Jun 17 2025 to Nov 17 2026; 360 daily rows cached). Long SPY next session if net call premium − net put premium > 0, else short: +0.001 [−0.066, +0.067], halves +0.054 / −0.051, long −0.008, short +0.012, 2x −0.045, below the random-side p95 (+0.009). Correlation with next-day open-to-close +0.05, with close-to-close +0.05; the day-over-day change −0.03. Daily tide says nothing about tomorrow.

## H24: Flux Field inner-band gate (coach request) — NOT A LEAD YET (right sign, too few days)
29 sessions (Oct 8-Nov 17; Nov 18 pulled but its 1-min bars are not archived yet), SPY + QQQ, random 1-min entries, Flux point of minute t−1.
- 30-minute exit: with-zone −0.035 (530), against −0.072 (545), inside −0.047 (1,245). With − against **+0.037 [−0.018, +0.083]**; long +0.036, short +0.033, first half +0.033, second +0.041: every cut has the predicted sign, but the CI includes 0, so it fails the pre-registered bar.
- Flat at 15:55: with − against +0.034 [−0.18, +0.22]; second half −0.012. Nothing.
- Price sat outside the inner band 46% of minutes (above 21%, below 25%).
- Level reclaim/loss (first close back over/under the level after 15+ minutes on the other side, hold to close): 84 trades, +0.016 [−0.07, +0.13]; long −0.093, short +0.119 (regime).
- Even if the gate is real, with-zone entries still lose after costs (−0.035): it is at best a filter that makes a losing entry lose less, not a rule. Keep growing the Flux archive (the Coach pulls 2 credits a day) and re-run at 60 sessions.

## Newsie shadow (day 1 of 20, 2026-11-18)
Newsie: SPY up 53, QQQ up 57; flags orb_vol normal, ema_vol caution, volspike normal, ema_vol_v2 caution; event 14:00 ET FOMC minutes.
- caution (drop eod holds spanning 14:00 ET): ema_vol and ema_vol_v2 QQQ +$1.47 each removed → −$2.94 vs actual.
- bias (keep only the favored side): orb_vol SPXU (short) −$5.14 removed → +$5.14; volspike UPRO long kept (−$8.77).
- sit_out: none issued.
One day; reported only. Newsie's call scores were not in yet (SUMMARY: 0 scored).

## Variants
H19 1, H20 2 (+fade), H21 2, H22 3 + exit pair, H23 2, H24 2 exits + reclaim (3), Newsie 3 flags x 4 desks (12): **26 new, running total 212.**
