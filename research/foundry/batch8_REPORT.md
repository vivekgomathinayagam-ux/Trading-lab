# Foundry batch 8 report (Researcher, Wed 2026-11-25 build run)

Pre-registration: `research/foundry/PREREG_batch8.md` (commit a5a1efd, before computing). Code `lab/foundry/batch8.py`, tests `lab/tests/test_foundry_batch8.py` (no look-ahead, costs, hand cases). Numbers: `research/foundry/batch8/summary.json`. Underlying signed % per trade, net of 0.046% round trip; CIs are day-block bootstrap 95%.

**Result: 0 of 6 decision cells passed. No desk change.**

## H30: open-reversal ("V") days (coach 11-23, LESSONS 55)
Gap ≥ 1%, a 1% flush against the gap by 09:55, then a 1% recovery off the extreme by 10:45.
- **Count: rare.** L5 (Alpaca 5-min, 1,732 sessions 2020-2026): 28 symbol-days (SPY 11, QQQ 17), 17 of them in 2020; 1-2 a year since (2021: 1, 2022: 5, 2023: 0, 2024: 2, 2025: 2, 2026: 1, the last being Nov 23). Below the pre-registered 30 per gap direction, so **no rule is built**.
- Entries at the V confirmation, flat 15:55 (L5, for the record only):

| cell | n | mean % | 95% CI | halves | random p95 |
|---|---|---|---|---|---|
| with the V, gap up (long) | 11 | +1.30 | [−1.16, +3.32] | +1.41 / +0.24 (10/1) | +1.97 |
| fade the V, gap up (short) | 11 | −1.40 | [−3.41, +1.07] | | |
| with the V, gap down (short) | 17 | +0.30 | [−0.45, +1.09] | +0.10 / +0.97 (13/4) | +1.11 |
| fade the V, gap down (long) | 17 | −0.39 | [−1.18, +0.36] | | |

"With the V" is positive but below its own random-entry p95 on those same violent days (any entry on a 2020-style day moves a lot). LESSONS 55's Nov 23 reading (nothing left after the V) is one day of the few; the 2020 days mostly trended on after the V. Too few days to say more.

## H31: impulse fade (IDEAS 11-12/13, coach 11-24)
After a 1.5% leg (session high vs the lowest low before it, or mirror), fade the first lower low (short) / higher high (long), stop just beyond the extreme, flat 15:55, entries 10:00-14:30.

| cell | archive | n | mean % | 95% CI | halves | 2x costs | random p95 |
|---|---|---|---|---|---|---|---|
| fade up-leg (short) | L5 2020-26 | 460 | **−0.129** | [−0.208, −0.047] | −0.129 / −0.131 | −0.175 | −0.121 |
| | L1 2022-26 | 313 | −0.117 | [−0.202, −0.022] | −0.110 / −0.129 | −0.163 | −0.131 |
| | Y1 Sep 28-Nov 25 | 12 | +0.309 | [+0.02, +0.57] | | | |
| fade down-leg (long) | L5 | 561 | −0.056 | [−0.135, +0.039] | −0.106 / +0.024 | −0.102 | −0.140 |
| | L1 | 394 | −0.022 | [−0.116, +0.076] | −0.046 / +0.009 | −0.068 | −0.122 |
| | Y1 | 20 | −0.311 | [−0.49, −0.13] | | | |

- **Refuted, both sides.** Fading an up-leg loses in every half of five years, CI below 0 (stopped out on 343 of 460: the leg usually resumes). Fading a down-leg is a coin flip less costs.
- The recent 2 months say the opposite (short side +0.31% on 12, long side −0.31% on 20): that is the Sep-Nov down-drift regime (LESSONS 3, 24) again, not edge. Same trap as batch 1.
- Fits LESSONS 22 (0.6% leg fade refuted) and extends it to 1.5% legs with a price-structure trigger.

## Newsie shadow (standing; 6 Newsie days, Nov 18-25; shadow only until 20)
Paper trades of the 4 desks on Newsie days, P&L in $ (`lab/news/shadow.py`, `research/foundry/batch8/newsie_shadow.json`):

| desk | trades | as traded | sit_out | caution (±15 min of an event, or holding through one) | caution = skip the day | bias (keep favoured side) |
|---|---|---|---|---|---|---|
| orb_vol | 2 | −27.81 | −27.81 | −5.14 | −5.14 | 0.00 |
| ema_vol | 4 | +6.94 | +6.94 | −5.01 | −5.01 | +8.72 |
| volspike | 6 | −2.32 | −2.32 | −6.14 | −8.77 | −23.48 |
| ema_vol_v2 | 4 | +5.84 | +5.84 | −6.11 | −6.11 | +7.62 |
| **all** | 16 | **−17.35** | −17.35 | **−22.40** | −25.03 | **−7.14** |

No sit_out flags yet. Caution flags as written would have cost $5 net (they helped orb_vol by $22.67 and removed ema/volspike winners). Bias would have saved $10 net: it removed orb_vol's Nov 18 SPXU (−$5.14) and Nov 24 UPRO (−$22.67) and the ema desks' Nov 23 SPY longs (−$1.78 each), but also volspike's Nov 25 QQQ long (+$21.16, itself a running-volume entry). Six days, n = 16 trades: no signal either way. Event parsing: times written "HH:MM ET" in event_risk, skipping items already out before the open and early-close notes.

## Variants
H30 8 (4 decision cells), H31 4 (2 decision cells), volume guard 6 filter settings (data, not a rule). Total this run: 18. Running total in `research/VARIANTS.md`.
