# LESSONS: what Compound City has learned (read first, every agent, every run)

This is the system's memory of what works, what doesn't, and why. Every lesson cites its evidence.
- **Who writes here:** the Session Coach (daily), the Researcher (Wed/Sat) and any interactive session.
- **How to change a lesson:** never delete one. When new evidence changes it, strike it through and add the update with a date.
- **Status tags:** `confirmed` held out of sample; `tentative` only in-sample or small n; `refuted` a tested idea that failed (kept so nobody re-tests it blindly).

## Market behaviour (SPY/QQQ intraday)
1. `confirmed` **The +5% target is almost never reachable intraday.** It hit 0 times in 89 backtest trades and 0 in 22 paper trades. Since 2010 SPY moved +5% in a day on 0.17% of days, and 3x ETFs on 3-10%. (exit study 2026-10-29; STATE)
2. `confirmed` **Flat by 15:55 beats holding overnight.** Holding gave −0.30%/trade vs +0.05%, with a worst gap of −3.4%. (research/exits/REPORT.md)
3. `tentative` **Sep 28 to Nov 2 was a down-drift regime.** Long from 09:45 to 15:55 averaged −0.13% a day on SPY/QQQ. Every trend rule's short side made money and its long side lost. That is regime, not edge: rules must be judged on both sides and on more than one regime. (foundry batch 1, 2026-11-03)
4. `confirmed` **The 0DTE GEX board does not predict the next 60-90 minutes:** no magnet, no gamma-regime range effect. (Skylit pilots 1 and 2)
5. `confirmed` **Options over-price SPY/QQQ next-day moves.** Realized moves are about 0.68-0.75x the priced 1-sigma, in both halves of 2 years. ~~That is a lead for defined-risk premium selling, but not yet proven after bid/ask.~~ (Skylit pilot 2) **Update 2026-11-04:** the premium is real, but the plain 1-sigma 1-day condor doesn't capture it: see 19.

## Our desks: why they miss moves
6. `confirmed` **The desks cannot go short SPY/QQQ directly; only the inverse ETFs give a short.**
   - Nov 2: SPY offered a 1.6% down-leg (10:28 to 15:58 ET) and all 4 trades were longs that lost.
   - Nov 3: the 5 entries were all long; none shorted the 13:30 ET breakdown.
   - Every new rule family must include a short side. (post-mortems 2026-11-02/03)
7. `confirmed` **Exits are the biggest leak.**
   - Non-CVD desks hold to 15:55 with no trailing exit, so they give back trends: Nov 3 volspike bought SPY 755.82 at 10:56 ET and the open trade was below entry by 15:00.
   - CVD exits are the opposite problem, too twitchy: Nov 3 cvd_spy held 3 minutes.
   - Fixed take-profits lost to baseline, and the ATR trail failed walk-forward. (exit study)
8. `tentative` **Entries that are already extended do worse,** as does very low ATR. Both held in both halves of the entry study, but neither passed as a filter. (research/entries/REPORT.md)

8b. `tentative` (see 23, 2026-11-04) **Late entries lose.** Every paper entry after 13:00 ET lost: 3 of 3, -$1.77, -$4.23, -$2.04 (Oct 27 ema_vol TQQQ 15:00, Oct 28 ema_vol SPXU 13:35, Nov 3 orb_vol QQQ 13:50 into an existing down-leg). n=3, so a lead only, not a rule. (coach 2026-11-03)

## Rule families tested (foundry batch 1, 5-min bars, 26 sessions, SPY+QQQ, costs 0.046% round trip)
9. `refuted` **Simple trend rules lose after costs:** Ripster cloud ride (F1 slow exit, F2 tight exit) and VWAP trend (F3).
   - 1-min sample (26 sessions): F2 +0.013%/trade, F3 +0.008%, F1 −0.006%. Gross edge is about +0.04-0.06%, roughly the 0.046% round-trip cost.
   - Wider 5-min sample (41 sessions, Sep 8-Nov 3): all negative. F1 −0.023% (177 trades), F2 −0.014% (243), F3 −0.023% (149).
   - Every one is negative in the first half and slightly positive in the second, which is regime drift, not edge.
   - Short sides beat long sides in both samples (the down-drift regime, lesson 3).
   - Don't re-test these as-is. Only with a new ingredient: a trend-day gate, fewer and bigger trades, or 3x-ETF execution. (foundry batch 1, 2026-11-03)
10. `refuted` **Fibonacci 50-61.8% pullback toward the session extreme (F5):**
   - It looked good on 26 sessions: 21 trades, +0.038%, 67% win.
   - It failed on 41 sessions: 49 trades, −0.050%, PF 0.64, negative in both halves.
   - The small first sample flattered it.
11. `refuted` **Fibonacci 38.2-50% pullbacks (F6) lose:** −0.061%/trade on both samples (37 and 73 trades). The 5-min CI is entirely below zero [−0.115, −0.006].
12. `refuted` **The VWAP trend-break reversal (F4) as written:** −0.015%/trade on both samples (39 and 63 trades). Its short side was positive (+0.04%) and its long side negative, which is regime again.

## Foundry batch 2 + condor study 1 (2026-11-04, `research/foundry/batch2_REPORT.md`)
19. `refuted` **A 1-day SPY iron condor at ±1 priced sigma with $5 wings loses after costs.**
   - 21 trades (Oct 5-Nov 2), real Skylit last prices: −$12.52 per condor at $0.02/leg, −$4.04 even with no slippage.
   - It won 81% of the time, but the average credit was $0.48 against a $4.52 max loss, and the 4 breaches (−$139 to −$427) erased it.
   - Its max loss is about 45% of a $1,000 account, so the 5% cap forbids it anyway.
   - Retest only with a new reason: wider short strikes with the credit ≥ 20% of the width, or $1 wings sized under the cap.
20. `refuted` **A giveback trail (exit at half of the best open profit, armed at +0.3% x leverage) doesn't fix lesson 7's leak.**
   - Desk entries: +0.0015% per trade, CI [−0.046, +0.054], with the two halves of opposite sign.
   - Random entries: worse than holding on both archives (−0.051 / −0.027).
   - It helped volspike (+0.18) and hurt ema_vol (−0.14): desk-specific, not a general exit.
21. `refuted` **The first hour's direction does not continue on "trend days" (range ≥ 1.2x, RVol ≥ 1x, VWAP slope agrees, measured at 10:30 ET).**
   - G1/G2/G3 were negative on both archives, worse than ungated.
   - The 5-17 gated days were too few for a strong verdict either way, but there is no sign of edge.
22. `refuted` **Reversal-day VWAP cross after a 0.6% leg:** +0.04 / +0.01% per trade (31 / 34 trades), below the random control, negative at 2x costs. Only its short side won (regime).
23. `tentative` **No new entries from 13:00 ET.**
   - Foundry entries from 13:00 lose −0.07% per trade on both archives (88 and 166 trades; CI below 0 on B).
   - Desk backtest entries from 13:00: 5 of 5 lost, but that is only 4 independent trades. Paper: 3 of 3 lost.
   - Entries before 11:30 are about 0, so the cutoff saves money; it does not make any.
   - Forward test from Nov 5 on the existing paper ledger: wrong if 10 paper entries from 13:00 average ≥ 0. Upgrades lesson 8b.
   **Update 2026-11-07 (Researcher, split by side, `research/foundry/batch3_REPORT.md`):** on batch 1-2 foundry trades, late longs (−0.09 to −0.13%/trade) are no worse than early longs (−0.09 to −0.12); late shorts (−0.02 to −0.04) are worse than early shorts (+0.03 to +0.11). So the 13:00 effect is mostly "shorts lose their edge late"; longs lose at every hour in this regime (24). Paper forward count: 2 entries from 13:00 since Nov 5 (the same ema_vol/ema_vol_v2 QQQ trade, −0.81/−0.80%), so 1 independent of 10. Since Oct 26 every paper entry from 13:00 has lost (5 independent trades).
24. `confirmed` **Five rule families in two batches show the same pattern:** shorts won and longs lost. Short-side "edge" from Sep-Nov 2026 must not be read as edge until a rising regime is in the sample. (batches 1-2)

## Data and infrastructure
13. `confirmed` **The Yahoo real-time feed can freeze silently.** Oct 30 it froze for 74 minutes and a paper exit used the stale price. PR #2 fixes this but awaits Vivek. (research/weekly/2026-W44.md)
14. `confirmed` **Only 26 sessions of 1-minute history exist** (Sep 28 onward, Yahoo's 30-day limit), so every intraday verdict is low-power. The fix is a long-history source: Alpaca's free plan has minute bars since 2016. (2026-11-03)
25. `confirmed` **One bad 1-minute bar can fake a trend leg.** SPY 10:00 ET on 2026-11-04 has a high of 775.64 (0.99% wick; the open/close were 767.26/768.02). The post-mortem then reported a 1.705% SPY up-leg and a 1.577% down-leg; from closes SPY's range was 0.8% (UPRO, QQQ and TQQQ legs agree with that, not with the post-mortem). It is the only bar in 10,920 SPY and 10,919 QQQ minutes with a wick over 0.4%. Check any SPY rule that uses bar highs/lows (breakout, range, stop) around that bar, and clean wicks before computing legs. (coach 2026-11-04, `research/coach/2026-11-04.md`)
   **Update 2026-11-05:** it recurred. SPY 13:10 ET on 2026-11-05 has a high of 744.50 against a 737.32 close (0.97% wick; QQQ the same minute has none), and the post-mortem's SPY best up-leg of 1.397% (13:04-13:10) is that bar; clean, it is 1.076% (10:53-11:29, like QQQ's). Two such bars in 11,310 SPY minutes, both on SPY only, both in the last two sessions: a feed issue, not noise. Clean wicks at ingest, not per report. (coach 2026-11-05)
   **Update 2026-11-07:** done for the post-mortems (`lab/foundry/postmortem.py` clips 1-min wicks beyond 0.4% x leverage of the body) and for batch 3 (0.4% on 1-min, 0.6% on 5-min; 2 bars clipped per archive). Nov 4/5 post-mortems rebuilt: SPY Nov 4 up-leg 1.108% (was 1.705), down 0.996% (was 1.577). Cleaning changed 4 batch-1 SPY trades on Nov 4 (all losers either way) and no F1-F4 signal at the Nov 5 13:10 bar. Batches 1-2 still read raw bars; the effect on their totals is a handful of trades.

26. `tentative` **On reversal days the long desks buy the fade.** 2026-11-06: SPY/QQQ/TQQQ topped at 09:53 (+1.0/+1.4/+4.2% from the open) and faded; the three paper longs entered after the top lost -$27.61 (cvd_tqqq 10:15 -$5.64, volspike QQQ 11:25 -$5.10, orb_vol UPRO 12:23 -$16.87), none above +0.2% open profit, and foundry longs won 1 of 23 (+0.034%). Foundry shorts won 3 of 4, all after 12:05. n = 1 day (3 independent paper trades); a lead, not a rule. Counter: cvd_spy's 10:39 long won +$2.44 the same day. Ties to 8 (extended entries) and 24 (regime). Needs a two-sided test before it means anything. (coach 2026-11-06)
   **Update 2026-11-07 (Researcher, H8):** the general version is not supported. A "stale-high" filter (long when the session high is 15+ min old and price is below VWAP; short mirror) made no difference on random entries on either archive (CIs straddle 0; on 1-min, stale longs did slightly better) or on 217 floor-lab desk entries (stale −0.005% vs fresh +0.002%, CI [−0.54, +0.44]). 26 stays a description of Nov 6, not a filter.

## Foundry batch 3 (2026-11-07, `research/foundry/batch3_REPORT.md`)
27. `refuted` **A two-sided opening-range break (09:30-09:45 range, close beyond it by 0.10%, stop at the other side) loses:** −0.049% (45 trades, 1-min) and −0.038% (63, 5-min) per trade, below the random control. Long side −0.18%, short +0.14% (regime, 24). The 0.30%-buffer cells looked positive (+0.08 to +0.10% on 5-min) only through Nov 5-6 shorts; without those two days every cell is negative. Closing the entry window earlier did not help: "until 15:25" beat "before 11:00" on both archives, and orb_vol's own backtest entries before 11:00 were worse (−0.44%, 13) than later ones (−0.16%, 6).
28. `refuted` **Prior-day high/low: break-and-hold loses, and the reject fade doesn't pay.** HOLD −0.183%/trade on 5-min (20 trades, CI [−0.31, −0.05]), −0.151% on 1-min, both sides and both halves negative. REJ −0.055% / +0.011%, 20% win rate, below the random control.
29. `tentative` **Big opening drives are rare and, so far, continue.** A 09:30-09:55 move of ≥ 0.5% (SPY) / 0.7% (QQQ) happened on 2 of 44 sessions per symbol, and all 4 drive days closed in the drive's direction; ≥ 0.9%/1.3% on 1 day each; a ≥ 1.5% impulse inside 45 min on 1-2 days. The failed-drive reversal (coach, Nov 6) had 2 trades: untestable here. Needs the long history (Alpaca).
30. `tentative` **This week the leak was entries, not exits.** Nov 2-6: 17 of 27 paper trades never reached +0.3% open profit; the market offered SPY legs summing +4.7% up / 8.4% down (QQQ 7.4 / 12.1) and the desks lost −$103.65 (−$91.37 without ema_vol_v2's duplicate trades). Refines 7 for this week: better exits can't fix trades that never go green. (Researcher, post-mortems Nov 2-6)
32. `tentative` **On a trend-up day the desks were on the right side and the leak was exits, with entries late.** 2026-11-09: SPY +1.44%, TQQQ +8.75% leg; 3 long paper trades all won (+$11.83) but captured 9-18% of the leg (cvd_tqqq sold after 6 min, +0.80% of 8.75%). Foundry holds captured more (F1 QQQ +0.94%, 32% of the leg; F2 tight exit +0.01 to +0.29%). Both foundry shorts lost (-0.34/-0.63%), the mirror of 24. n = 1 day; it contradicts 30 only for trend days (0 of 3 trades below +0.3% MFE; Nov 2-9: 17 of 30). Consistent with 20 (trails lose to holds), but 21 says the day type is not knowable at 10:30, so this is a description, not a rule. Needs the regime-split test (hold vs CVD sell on up days and on down days). (coach 2026-11-09)

33. `tentative` **Longs bought 0.3%+ under QQQ's running high lose, on the days that fade.** Oct 28-Nov 10 (10 sessions, QQQ 1-min closes): 16 independent paper long entries met that test; 5 won, 11 lost, net about -$95.7; at least one such long lost on 5 of 10 days (Nov 2, 4, 5, 6, 10; Nov 10: cvd_tqqq 10:21 -$22.78, ema_vol QQQ 10:15 -$4.07). 4 of the 5 days were down or reversal days, so this is partly LESSON 24 (regime), and the earlier stale-high filter (26, H8) did not help on random entries; this measures distance under the high, not its age. Entries within 0.3% of the high had no such pattern (Nov 9 all won). Also Nov 10: on the V-reversal day the tight exit (F2 QQQ short +0.57%) beat the wide stop (F1 -0.55%), the reverse of Nov 9, so exit ranking flips with day shape (n=2, see 32). n=10 sessions, not tested against random entries; a lead for the Researcher. (coach 2026-11-10)
   **Update 2026-11-11 (Researcher, batch 4 H9, `research/foundry/batch4_REPORT.md`):** as a filter it is refuted. On random entries at 0.3% from the extreme, far − near was −0.017% on A but +0.012% on B (1,536 / 2,208 entries), halves disagree, and shorts don't mirror longs. Far longs are worse at 0.75% on both archives (−0.07 / −0.10) while far shorts are not: that is LESSONS 24's regime. 33 stays a description of the losing paper longs, not a rule.

## Foundry batch 4 (2026-11-11, `research/foundry/batch4_REPORT.md`)
34. `refuted` **A fail-fast exit (out at 15 minutes if the trade never reached +0.10%) does nothing.** Paired against the same entries: random +0.000 / +0.002% per trade (CIs ±0.012), batch 1-3 rule entries −0.001 / +0.003%, floor-lab desk entries −0.064% (230; it hurt volspike and orb_vol). Long and short sides have opposite signs. Slow starters are not reliably losers, so LESSONS 30's "entries that never go green" can't be cut early at 15 min.
35. `tentative` **The best exit flips with the day's shape, and the day's shape is hindsight.** Both archives, every cell: the wide F1 exit beats the tight F2 exit only when the day trends the trade's way (long-up +0.14 vs +0.03, short-down +0.59 vs +0.20 on B); F2 loses less on V, chop and counter-trend days. CVD desk entries: holding cvd_tqqq to 15:55 beats its CVD sell on up days (+1.61 vs +0.55, n=9) but is a disaster on down days (−4.04 vs −0.24, n=8); over all 29 the CVD sell is +0.20% vs −0.66% for holding. Keep the CVD exit; a "let winners run" exit needs a day-type signal known at entry, and LESSONS 21 found none at 10:30. Settles coach items 2026-11-09 (1) and 2026-11-10 (2), and explains 32.
36. `tentative` **Trading with a 1% move from the open looks positive but rests on one day.** H10: buying 1% under the open and shorting 1% over it both lost (−0.14 to −0.18% vs normal entries, both archives, both sides; 10-14 distinct days, CIs include 0). Its mirror, H13 (first 5-min close ≥ 1% from the open 09:45-14:00, trade with it, stop at the open/entry midpoint): +0.37 / +0.35% per trade (17 / 20 trades), above the random control, but A's CI is [−0.17, +1.03], B's first half is −0.05, and without Nov 5-6 it is +0.07 / +0.09%. Fits 29 (big drives continue). Suggested by the same archives, so it is a forward test only: from Nov 12, wrong if its first 15 new trades average ≤ 0.
37. `tentative` (arithmetic; confirmed once the Accountant re-derives it, BOARD 2026-11-11) **At a $1,000 account the 5% cap forbids every SPY iron condor except near-ATM flies.** Max loss = wing width x 100 − credit; the cap is $50. With $1 wings the credit must be ≥ $0.50 (50% of the width); a "credit ≥ 20% of width" condor (IDEAS condor v2) loses up to $80 per contract and needs ≥ $1,600 of equity. Paper is sized as live (rule 7), so condor v2 waits for a bigger live account. (arithmetic, 2026-11-11)

## Data and infrastructure (continued)
31. `confirmed` **The paper bot skips real signals when Yahoo delivers two bars at once.** It calls a signal bar "stale" unless it is the newest bar in the step. Railway logs: Nov 5 09:55 ET, cvd_tqqq's and cvd_spy's 09:53 signals skipped (the lab took cvd_tqqq at 09:54; paper entered at 10:09); Nov 2, CVD signals at 10:08 and 10:11 skipped (those were 5-7 min late, truly stale). A cause of the parity gaps (17 of 29 match, Nov 2-6). Fix: draft PR #3, waiting on Vivek (City Hall `d-fresh-signal`). (Researcher 2026-11-07)

15. `confirmed` **Position size makes the P&L tiny.** A $1,000 desk buys 1 SPY share, so even a perfect 0.8% SPY day pays about $6. Edge has to be proven in % terms first; dollars come from size, 3x ETFs or options, under the money rules.

## How we work (process lessons)
16. **Two samples beat one.** A rule that looks fine on 26 sessions can fail on 41 (F5). Every test runs on both archives before anyone believes it.
17. **Every session gets a post-mortem** (`research/postmortem/<day>.md` on branch `data`): what the market offered (best up and down legs), what each desk did, what it gave back, and what the foundry rules would have done. The Coach turns that into at most one lesson here per day, only when it is new.
18. **Hindsight shows opportunity; it never picks rules.** A rule changes only through a pre-registered test. Today's chart always looks obvious; the question is whether the rule works across many days.
