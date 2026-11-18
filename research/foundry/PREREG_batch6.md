# Foundry batch 6: pre-registration (Researcher, Wed 2026-11-18 build run)

Written and committed BEFORE any of these numbers were computed. Research only; nothing here trades.

## Data
- **L** = long Alpaca 5-min archive, SPY + QQQ, 2020-01-02 to 2026-11-17 (1,729 sessions), `data:backtests/data/alpaca5m/`. Halves: **L1** = first 864 sessions, **L2** = the rest. 2026 sessions are also reported alone (holdout-style; none of these rules was tuned on 2020-2025).
- **A** = 1-min ETF archive (Sep 28 on) resampled to 5-min; **B** = 5-min ETF archive (Sep 8 on). Reported for consistency only: they are where H13/H20 were found, so they cannot confirm them.
- Wick cleaning as batch 3 (5-min: clip wicks beyond 0.6% of the body).
- Costs: 0.046% round trip (2 x (0.02% slip + 0.003% fee)); every rule also at 2x costs.
- Fills: signal at a bar's close, fill at the next bar's open. Flat by the 15:50 bar's close (last 5-min bar before 15:55).
- Random control: 3 random entries per session per symbol, random side, seeds 21-28, same stop/exit as the rule under test; the rule must beat the 95th percentile of the mean of n random trades (n = rule's trade count, 500 draws).

## Pass bar (every rule hypothesis)
All of: mean net > 0 on L; bootstrap 95% CI lower bound > 0 on L; mean > 0 in L1 AND L2; long side and short side each > 0 on L; mean at 2x costs > 0; above the random-control p95. A rule that passes goes to paper as a new desk key (SPY/QQQ via UPRO/TQQQ for longs, SPXU/SQQQ for shorts).

## Hypotheses
- **H19: H13 on the long archive.** First 5-min close 09:45-14:00 at >= 1% from the 09:30 open (SPY or QQQ separately), trade with it, stop at the midpoint of the open and the signal close, flat at the close. Forward record so far 1 win in 6 (−0.32%). Prediction if real: passes the bar. If it fails the bar on L, LESSONS 36 is refuted and the forward test ends.
- **H20: 0.5% morning continuation (LESSONS 42).** First 5-min close 09:45-10:25 with |close/open − 1| >= 0.5%; trade with it, hold to the close. Primary: no stop. Secondary (reported): 0.5% stop. The fade (opposite side) is reported, not a separate test.
- **H21: the 13:00 cutoff (LESSONS 23).** Random entries (above), 0.5% stop, flat at the close. Statistic: mean(entries from 13:00) − mean(09:45-12:55 entries), per side, with a day-block bootstrap CI. Confirmed if the difference is < 0 with the CI below 0 on L and negative in L1 and L2 for both sides; refuted if the CI includes 0 or halves disagree. (Mechanical caveat to report: late entries hold fewer bars, so their variance is smaller; compare per-trade means, not totals.)
- **H22: day-type marker known at 10:30 (QUEUE 1).** At the 10:25 bar close: first-hour range FR = (high − low)/open over 09:30-10:25; R = FR / mean(FR of the prior 20 sessions); direction d = sign(close − open). Trade with d at the next open, 0.5% stop, flat at the close. Primary gate R >= 1.5; R >= 1.25 and R >= 2.0 reported. Also the paired question that motivated it (LESSONS 35): on gated days, does holding to the close beat a tight exit (5/12-EMA cross exit of F2)? Reported, not a pass/fail.
- **H23: Skylit market tide (daily).** Daily net premium flow N_t = net call premium − net put premium (market-wide). Rule: if N_t > 0 go long SPY at the next session's open, else short, flat at that session's close (also next-day close-to-close reported). Bar: as above, on the ~250 days the pull returns, halves by date; also correlation of N_t (and its 1-day change) with the next day's open-to-close. If the tool has no daily history, report that and stop.
- **H24: Flux Field inner-band gate (coach, BOARD 2026-11-17).** 1-min Flux Field for SPY and QQQ, the 30 sessions Skylit returns (Oct 8 to Nov 18). Decision minute t uses the Flux point of minute t−1 (no look-ahead even if a point is stamped at its bar's start). Zone: above = close > inner.upper; below = close < inner.lower; inside otherwise. Random 1-min entries 09:45-15:00 (5 per session per symbol per seed, seeds 21-28, random side), fill next minute's open, two exits: 30-minute time exit and flat at 15:55, 0.5% stop. Statistic: mean(with-zone: long when above, short when below) − mean(against-zone), and with-zone − inside. Lead if with − against > 0 for both sides and both halves (15 sessions each) with a day-block CI above 0. 30 sessions is low power: a pass makes it a candidate for a pre-registered `skylit_v1` rule, not a desk by itself. Also the level-reclaim rule: long on the first close back above the level after 15+ minutes below (short mirror), flat at 15:55, 0.5% stop; reported with n.

## Newsie shadow (standing, from 2026-11-18)
For each Newsie day: replay each paper desk's trades that day with (a) sit_out = remove all trades, (b) caution = remove entries inside ±15 min of an event_risk time and remove eod holds that span it, (c) bias = keep only trades on the side Newsie favored (inverse ETFs count as short). Report the change in P&L per desk. Shadow only until 20+ Newsie days.

## Variants counted
H19 1, H20 2 (+fade reported), H21 2 sides, H22 3 gates + 1 exit comparison, H23 2, H24 2 exits + 1 reclaim rule, Newsie 3 flags x 4 desks. Counted in research/VARIANTS.md.
