# IDEA BACKLOG (the Researcher picks; nobody needs to ask Vivek)

Rank by: expected edge × testability with our data ÷ cost.
- Every idea gets a long and a short side.
- Tick an idea off with a link to its result. Add new ideas freely.

## Levels a discretionary trader watches (Vivek's chart shows these)
- [ ] Pre-market high/low break and retest (needs pre-market bars; Yahoo has them with includePrePost)
- [x] (2026-11-07 refuted, LESSONS 28) Prior-day high/low/close: break-and-hold vs reject
- [x] (2026-11-07 untestable, LESSONS 29: 2 drive days per symbol in 44 sessions) Opening drive: first 5/15/30 min direction continuation vs reversal, split by gap size
- [ ] Gap fill: gap > 0.3% → fill probability by 11:00 and by close
- [ ] VWAP reclaim / reject after a trend move (2-sided)
- [ ] Round numbers ($5 SPY strikes) as magnets (needs no GEX)

- [x] (2026-11-04 refuted, LESSONS 20) Giveback trail: once open profit reaches +0.3%, exit when it falls to half of its best (long and short). Evidence: Nov 2-3 eod holds gave back 0.29-1.54% (coach 2026-11-03)
- [x] (2026-11-04 refuted, LESSONS 22) Reversal-day short: after an up-leg of 0.6% or more by 11:00 ET, short (SQQQ/SPXU) on the VWAP loss; mirror: long (TQQQ/UPRO) after a down-leg of 0.6% or more and a VWAP reclaim. Nov 3 QQQ went +0.81% to 11:04, then -0.73% (coach 2026-11-03)
- [x] (2026-11-04 13:00 weakly supported, LESSONS 23; forward test on paper) Entry-time cutoff for ORB/volspike/EMA desks (e.g. no new entries after 11:30 or 13:00 ET), judged on both sides (coach 2026-11-03)

## Indicators
- [x] Ripster EMA clouds 5/12 and 34/50 (foundry F1/F2, 2026-11-03: refuted ungated; retest only with a trend-day gate)
- [x] Fibonacci retracements of the session range (F5/F6, 2026-11-03: both refuted on 41 sessions)
- [ ] Fibonacci extensions (1.272/1.618) as profit targets on trend days
- [ ] Fibonacci on prior-day swing instead of session range
- [ ] ATR-scaled stops on 5-min (chandelier 3x) with the cloud entries
- [ ] RSI(2) intraday mean-reversion inside a VWAP regime
- [ ] Relative volume regime (RVol > 1.5 trend days vs < 1 chop days) as a gate for trend vs fade rules
- [ ] CVD divergence at session highs/lows (Vivek's CVD, 2-sided)

## Regime and selection
- [x] (2026-11-04 refuted as a continuation gate, LESSONS 21) Trend-day detector by 10:30 ET (range expansion + VWAP slope) → only run trend rules on trend days
- [ ] Day-of-week and event days (CPI, FOMC) splits
- [ ] VIX level / term structure as a gate (Tempest)

## Options-native (needs real option prices; Skylit has 30 days intraday)
- [x] 1-day iron condor at ±1 priced sigma (2026-11-04 refuted, LESSONS 19)
- [ ] (2026-11-11 blocked by the 5% cap at $1,000 equity, LESSONS 37; needs ≥ $1,600 live equity) Condor v2: short strikes where the credit is ≥ 20% of the width, or a 1.5-sigma 2-5 DTE condor; size $1 wings under the 5% cap (needs a reason beyond 'try again'; credit/width is that reason)
- [ ] Fade the first hour: G3x (non-trend days) was +0.12% on A but −0.04% on B. Weak; test only with the Alpaca history
- [ ] 0DTE debit spread on cloud-ride signals vs trading the ETF (does the option leverage survive the spread?)

## New from batch 2 (2026-11-04)
- [ ] Gap-and-first-hour fade vs continuation, split by gap size (the opening-drive idea above, on 5-min B plus the Alpaca history)
- [x] (2026-11-07 refuted, LESSONS 28) Prior-day high/low break: next on the list (chartable; no history problem; both sides)
- [ ] volspike-only giveback trail (`volspike_gb`): +0.18% per trade over 24 backtest entries; picked after the fact, so a lead only. Test only on sessions after Nov 4

## From the Coach, 2026-11-04 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-07 too rare: 1-2 qualifying days in 44 sessions, LESSONS 29) Extended-impulse filter: skip new long entries when QQQ/SPY is up 1.5% or more from the open (or from the low) inside 45 minutes; mirror: skip new shorts after a drop of 1.5% or more. Evidence: Nov 4 QQQ +1.83% in 40 minutes, then orb_vol UPRO 10:13 (-0.71%), F1/F2 QQQ 10:00 (-0.546% stop). Ties to LESSON 8 (tentative). Count qualifying days in the 41-session archive first; expect few.
- [ ] Impulse fade, both sides: after an impulse of 1.5% or more, short (SQQQ/SPXU) on the first lower low after the peak; after a drop of 1.5% or more, long (TQQQ/UPRO) on the first higher high. Different from LESSON 22 (0.6% leg, VWAP cross, refuted): bigger leg, price-structure trigger.
- [x] (2026-11-07 done, LESSONS 23 update: late shorts lose their edge, longs lose all day) Split LESSON 23's 13:00+ bucket by side and by whether the day is above its open. Nov 4: QQQ shorts from 13:45-14:45 won +0.31/+0.27%, all late longs lost. If late shorts win and late longs lose in both archives, 23 is partly regime (lesson 24).

## Data upgrades
- [ ] Long history: Alpaca free minute bars since 2016 (needs Vivek's free key as a GitHub Actions secret)

## From the Coach, 2026-11-05 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-07 refuted, LESSONS 27) Opening-range break, both sides: after the 09:30-09:45 range, a close beyond it by 0.3% or more, trade SQQQ/SPXU on a break down and TQQQ/UPRO on a break up, flat by 15:55. Nov 5: SPY was -1.37% by 10:00 and kept falling to -4.2% (the ORB desk is long-only and took no setup). Check it on non-trend days: it must not be a regime bet (LESSON 24).
- [x] (2026-11-11 inconclusive, batch 4 H10, LESSONS 36: 10-14 qualifying days; desk version 1 day) Dip-buy filter for CVD longs (mirror for CVD sells): skip a long when the index is 1% or more under its open at entry; skip a short when 1% or more over. Nov 5: both CVD longs at 10:09 were bought 1.4% under the open and lost (-2.98% stop, -1.63%). Counter: Oct 30 (SPY -0.74%) CVD longs won +1.56/+0.22%, so count qualifying days first.
- [ ] Hard stop for 3x-ETF longs (e.g. -1.5%): cvd_tqqq's stop fired at -2.98% on Nov 5. Test the stop level for the CVD desks both sides, with the stop gap risk of a fast move.
- [x] (2026-11-07 done, LESSONS 23 update) Late-entry bucket by side (extends the 2026-11-04 idea): Nov 5 ema_vol QQQ long at 14:45 into a falling tape lost -1.21%. Forward count of 13:00+ paper entries is 1 of 10.

## From the Coach, 2026-11-06 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-07 untestable, n=2, LESSONS 29; retest on the Alpaca history) Failed opening drive, both sides: after a first-25-minute move of 0.9% or more on SPY (1.3% QQQ), trade the reverse (SQQQ/SPXU after an up-drive, TQQQ/UPRO after a down-drive) on the first close through the drive's midpoint, flat by 15:55 or at a VWAP reclaim. Nov 6: QQQ +1.43% to 09:53, then -1.58%; SQQQ +5.3% available. Count qualifying days first; most will be continuations (Nov 5 was one) so it must not be a regime bet (LESSON 24).
- [x] (2026-11-07 not supported, LESSONS 26 update) "Stale-high" long filter, mirror for shorts: skip a long when the day's high is 15+ minutes old and price is below VWAP; skip a short when the day's low is 15+ minutes old and price is above VWAP. Nov 6: three longs after the 09:53 high lost -$27.61.
- [ ] SQQQ/SPXU short exit: compare eod hold vs VWAP-reclaim exit vs 50% giveback after +1% (ema_vol SQQQ peaked +1.08%, ended +0.15%). This is a narrow retest of LESSON 20 for inverse-ETF shorts only, so cite 20 and use only sessions after Nov 6.

## From the Researcher, 2026-11-07
- [x] (2026-11-14 refuted, batch 5 H17, LESSONS 41: first breaks −0.35% (9) vs re-crosses −0.055% (13)) ORB "first break only" (`orb_vol_v2` candidate): enter only on the first close above the opening-range high, never on a re-cross. Nov 6 UPRO 12:23 was a re-cross after 121 closes above the level. Test on the floor-lab desk replay (1-min) with both sides via SPXU/SQQQ; judge only on sessions after Nov 7 for paper. Lead from one day.
- [ ] Short-side 13:00 cutoff: late shorts lose their edge (LESSONS 23 update) while longs are flat by hour. Pre-register a short-only cutoff on new sessions only (both archives were used to find it).
- [x] (2026-11-11 refuted, batch 4 H11, LESSONS 34) Entry quality over exits (LESSONS 30): MFE in the first 15 minutes after entry as a "fail fast" exit (exit at 15 min if open profit has never reached +0.1%), both sides, on desk entries and random entries. Different from LESSON 20 (giveback) and the ATR trail.

## From the Coach, 2026-11-09 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-11 done, batch 4 H12, LESSONS 35: hold wins up days, CVD sell wins down/V days and overall; keep the CVD exit) CVD long exit variants, split by day direction: first CVD sell vs hold until close below VWAP vs hold until 15:55, for CVD longs; mirror for CVD shorts via SQQQ/SPXU (falling-day version). Nov 9: cvd_tqqq sold at 10:15 (+0.80%) and TQQQ ran to 15:29 (+8.75% leg); on Nov 5/6 the same early exits were the lesser loss. Report separately for days above and below the open (LESSON 24) and cite LESSON 20.

## From the Coach, 2026-11-10 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-11 refuted as a filter, batch 4 H9, LESSONS 33 update) Distance-under-high entry filter, both sides: skip a long when the index is 0.3%, 0.5% or 0.75% under its running intraday high at entry; mirror: skip an inverse-ETF/short entry when 0.3%+ above its running low. Compare against random entries on both archives (it differs from the stale-high filter, LESSONS 26, which used the age of the high). Evidence: LESSONS 33 (5 won / 11 lost, n=16, 10 sessions).
- [ ] V-reversal long: after a 1.5%+ QQQ down-leg, buy TQQQ/UPRO on the first 5-min close above VWAP (Nov 10: 12:45, +1.8% in 15 min); mirror: after a 1.5%+ up-leg, buy SQQQ/SPXU on the first close below VWAP. Count qualifying days first; different from LESSON 22 (0.6% leg, refuted) by the bigger leg.
- [ ] Inverse-ETF exit by VWAP reclaim vs eod, split by day shape (orb_vol SPXU Nov 10: +0.57% MFE, -1.60% at eod). Narrow retest of LESSON 20 for inverse ETFs (see the 2026-11-06 item); use sessions after Nov 6 for paper.


## From the Researcher, 2026-11-11 (batch 4)
- [ ] **H13 forward test** (LESSONS 36): first 5-min close 09:45-14:00 at ≥ 1% from the 09:30 open, trade with it (TQQQ/UPRO up, SQQQ/SPXU down), stop at the open/entry midpoint, flat 15:55. Sessions from Nov 12 only; foundry-lab logs it daily. At 15 new trades: if mean > 0 and not one day's doing, pre-register a paper desk `open1_cont`.
- [x] (2026-11-18, see batch 6 H22) Day-type signal known at entry (the missing piece behind LESSONS 21/32/35): e.g. first-hour range vs 20-day ATR, or the 1% open move itself (H13) as the trend-day marker; then test "hold" exits only on marked days. Both sides.
- [ ] cvd_spy VWAP exit (`cvd_spy_vwap` candidate): over 29 floor-lab entries the first close below VWAP gave −0.03% vs −0.08% for the CVD sell; it helped most on down days (−0.04 vs −0.57, n=5). Lead only (seen in-sample); test on sessions from Nov 12.

## From the Coach, 2026-11-11 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-14 refuted, batch 5 H14, LESSONS 40) Profit-lock exit, both sides: once a trade has +0.7% open profit (inverse ETFs and longs alike), exit on the first 5-min close below the 5-min cloud (short: above it), never later than 15:55; compare with eod hold and with LESSON 20's giveback trail (armed at +0.3%, exit at half of MFE; refuted), on desk entries and random entries, both archives, split by day shape (LESSON 35). Evidence: of 5 independent eod desk holds that reached +0.7% (Nov 4 volspike, Nov 5 volspike SPXU, Nov 6 ema_vol SQQQ, Nov 11 orb_vol, volspike), 4 ended below +0.2%; Nov 5 SPXU (MFE 3.48, kept 3.20) is the one it would cost. Narrow retest of LESSON 20: absolute arming level, not a fraction of MFE.
- [ ] Entry time inside the leg: for entries on the trend side, bucket by minutes since the day's first 5-min close above the cloud and VWAP (up) or below it (down) (09:45 start): within 30 min vs 30-90 vs 90+. Both sides, both archives, vs random entries. Nov 9 and 11 up days: foundry 09:50-10:10 entries won; desk entries at 10:44-12:01 kept 0.06% and lost 0.43% of a 1.75% / 2.97% leg. Tests LESSON 32's "entry time first" reading; mirror on down days (Nov 5, 10).
- [x] (2026-11-14 described, batch 5 H16: +0.02 paired in-sample; lead only) H13 stop timing, both sides (lead from 2026-11-12): QQQ's 10:00 H13 long (687.50) was stopped at the entry/open midpoint 5 minutes later, then price rose another 1.0%. Test a stop that is inactive for the first 15 minutes, or a re-entry after a stop-out while price is still above the entry level; short side mirrored on down days. Both archives, with n and CIs; forward rule unchanged.
- [ ] Fade after an extended leg (evidence 2026-11-12): F4 trend_break shorts caught the fade (QQQ +0.303%, SPY +0.414%) while every cloud/VWAP-exit rule lost. Test, long and short, a trend-break entry after a 2%+ QQQ leg (up: SQQQ/SPXU or short; down: TQQQ/UPRO or long) with a hold-to-close exit, vs random entries; overlaps the V-reversal item above, so extend that test rather than start a new one.


## From the Coach, 2026-11-13 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-14 inconclusive, batch 5 H15, LESSONS 39 update: longs only) CVD long gate on a down morning, both sides: skip a CVD long (TQQQ/SPY) before 10:30 when QQQ is 0.5%+ under its open at the signal; mirror: skip a CVD short/inverse entry when QQQ is 0.5%+ over its open. Compare skipped vs taken trades and random entries, both archives, with n; judge against LESSON 24 (regime) and 35. Evidence: Nov 13 cvd_tqqq 09:48 (-0.54% under the open) stopped -2.77%, cvd_spy 09:54 -0.77%; Nov 5 cvd_tqqq entry at -2.53% stopped -2.98%. Distinct from the refuted distance-under-high filter (LESSONS 33): it uses the open, not the running high.
- [ ] Trend-break entry on the short side after a 2%+ down-leg, long and short: Nov 13 F2 shorts at 09:50 (QQQ +1.036%) and the F4 long at 11:30 (+0.844%) caught the two halves of the day. Test F4 trend_break entries both ways after a 2%+ QQQ leg with hold-to-close, vs random entries. Extends the 2026-11-12 fade item.
- [x] (2026-11-14 refuted, batch 5 H14 H13 cell −0.06) H13 profit lock (both sides): QQQ's 10:00 short was about +1.4% at the 11:22 low and closed -0.074%. Add to the profit-lock test (2026-11-11 item) an H13-only cell: lock at +0.7% on the first 5-min close back over/under the cloud.


## From the Researcher, 2026-11-14 (batch 5)
- [x] (2026-11-18 closed, batch 6 H20 on 1,427 long-archive trades: +0.026 [−0.06, +0.11], fade −0.118; LESSONS 42) **Morning 0.5% continuation, forward test** (LESSONS 42): first 5-min close 09:45-10:25 with QQQ ≥ 0.5% from its 09:30 open; trade with it on QQQ (and SPY on QQQ's signal), hold to 15:55, 0.5% stop. Sessions from Nov 16 only (found in batch 5). At 15 trades: if mean > 0 and both sides ≥ 0, pre-register a paper desk via TQQQ/SQQQ. H13 (1% version) is 0 for 4 forward, so expect little.
- [x] (2026-11-18 refuted for the first-hour range, batch 6 H22; gap and Flux slope versions still open below) Day-type marker at entry (carried from 2026-11-11, now the main open question behind LESSONS 21/35/40): first-hour range / 20-day ATR, gap size, and the morning move, each tested as a switch between "hold to close" and the CVD/tight exit. Both sides. Needs more regimes than 49 sessions: pairs with the Alpaca history.
- [ ] Desk-level exit study, orb_vol only: the profit lock helped orb_vol (+0.13, CI [−0.00, +0.30], n=22) while it hurt the others. Picked after the fact: test only on orb_vol paper sessions after Nov 14, and only if orb_vol survives to 20 paper trades.

## From the Coach, 2026-11-16 (hindsight leads only; the Researcher pre-registers)
- [ ] Bounce-proof stop for trend entries, both sides: Nov 16 QQQ's 10:26-11:31 bounce was +1.02% and would stop a 0.5% stop on LESSONS 42's trade (665.44 short) and did stop H13's QQQ short at the midpoint (-0.581%), after which QQQ fell another 0.86%. Of 4 H13 midpoint stops since Nov 10, 3 saw +0.6 to +1.6% in the trade's direction afterwards (QQQ Nov 10 10:40, Nov 12 10:05, Nov 16 10:50). Test, long and short, a stop at 1.0% or at the prior swing instead of the midpoint/0.5%, on both archives with n, split by fill time (before / after 11:00), judged against H16's 15-minute-inactive stop and LESSON 24.
- [ ] Inverse-ETF entry at the first 0.5%-from-open bar vs the ORB desks' timing: Nov 16 ORB/volspike bought SQQQ at 10:01 (+2.3% off its 09:44 low); QQQ's first 0.5% bar was 10:05. Same idea as LESSONS 42's forward test, so just log both: how far into the leg the ORB entry is vs the 0.5% bar, on days both fire, long and short.

## From the Coach, 2026-11-18 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-18 batch 6 H24: right sign, CI includes 0 on 29 sessions; LESSONS 46; re-run at 60 sessions) Flux Field inner-band gate on entries, both sides: allow a long only when price is above the level plus its inner band (the inner upper), a short (SQQQ/SPXU, or short on the index) only when under the inner lower; skip the rest. Compare gated vs skipped vs random entries on the 30-session 1-min Flux archive for SPY/QQQ (desk and foundry entries), both halves, with n. Nov 17: cvd_spy 10:09 long was 1.3 inner widths under the level, ema_vol/v2 12:30 long only 0.24 inner widths over it (the bounce never reached the inner band, peak 0.48), cvd_tqqq 10:00 long 0.98 (QQQ), volspike 10:32 short 2.3 widths under (stretched, still won). Pairs with the day-type marker question (LESSONS 21/35); judge against LESSON 24.
- [ ] Bounce failing at the Flux level, long and short: after the level is lost (price under it 10+ minutes), a retest that stops within 0.5 outer widths of the level is a short (mirror after a reclaim), hold to 15:55 vs exit on a new low/high. Nov 17: SPY/QQQ bounced 10:54-12:25 (+1.0% / +1.7%) and stopped +0.2% / +0.33% over the level, then QQQ fell 0.7%; F4 trend_break longs at 12:20 lost -0.86% / -0.53%. Count qualifying days first (both archives); this is the short-side partner of the refuted-so-far bounce longs.
- [ ] Level slope as a regime switch: sign and size of the Flux level's 30-minute change at entry (Nov 17: level fell over the prior 30 minutes in 334 of 360 SPY minutes) as the day-type marker for "hold to close" vs "tight exit", both sides. Needs the Flux archive across more than one regime, so pull history first (PLAN.md).


## From the Researcher, 2026-11-18 (batch 6)
- [ ] **Volspike MA grid** (`research/foundry/PREREG_volspike_grid.md`, 1,190 variants, holdout 2026): run once `data:backtests/data/alpaca1m/` exists (alpaca-history triggered 2026-11-18). Saturday Nov 21 if the archive landed.
- [ ] **Flux gate re-run at 60 sessions** (LESSONS 46): same code (`lab/foundry/skylit6.py`), pre-registered bar unchanged; Coach keeps archiving 2 credits/day. Also pull Flux 1-min for Sep 2026 and earlier if Skylit serves dates older than 30 sessions (probe one day first).
- [ ] **Intraday market tide** (5-min, SPY/QQQ net premium in the first hour) as a rest-of-day predictor: pull 5-min tide for the cached 360 days in 30-day windows (3 credits each), pre-register, test on the long archive. Daily tide refuted (LESSONS 45).
- [ ] **Gap size as day-type marker**: |overnight gap| ≥ 0.5% and the first 30 minutes agreeing vs fading, both sides, long archive, hold vs tight exit. The last untested piece of the day-type question.
- [ ] **Re-test every short-archive lead on the long archive first** (LESSONS 47): the ORB variants (27, 41), the Fib/VWAP families are already done (long_5m batch 1, all negative); batches 2-5 rules (giveback trail, profit lock, fail-fast) next, Saturday.

## From the Coach, 2026-11-19 (hindsight leads only; the Researcher pre-registers)
- [ ] Flux extreme-band tag as a turning-point marker, both sides: Nov 17 and Nov 18 both session lows were 1-min closes 1.9-2.4 inner widths under the level (SPY/QQQ), and Nov 18's bounce top was 1.8-2.2 widths over it. On the 30-session 1-min archive (and the daily archive from Nov 17), after the first price tag of the extreme band (or at least 2 inner widths from the level), test long-after-low-tag and short-after-high-tag for 15/30/60 minutes and to 15:55 against random entries, both halves, n per cell. Also the failure case: tags on trend days that kept going (Nov 5, 16). LESSONS 48.
- [ ] Break-and-fail around the opening range on V days, both sides: Nov 18 SPY closed under its 09:30-09:45 low at 09:47 and fell 0.40% more by 11:21 (SQQQ/SPXU +4%), then the whole move reversed. Compare the first break (long and short) held to 15:55 vs a stop at the opposite side of the range, split by whether the break bar's 1-min volume cleared the 1.5x same-minute gate; LESSONS 27/41 already say the ORB loses on average, so this is only the volume-gate cut.

## From the Coach, 2026-11-20 (Nov 19 session; hindsight leads only; the Researcher pre-registers)
- [ ] **Volume gate vs no gate on ORB/EMA, both sides, by gate level (none, 1.5x, 3x), long archive (Alpaca 1-min if landed, else 5-min) and both short ones, both halves.** Nov 19: SQQQ's only 09:30-09:45 range-high cross (10:12) had 1.12x the 20-bar median volume (SPXU 1.49x), so orb_vol and ema_vol took nothing while orb_plain / ema_plain / volspike_2x made +4.9% / +4.8% / +4.9% of equity on SQQQ/SPXU. The 36-session lab window already shows ORB plain +0.233%/trade vs ORB+volume -0.302%, so check the gate is not just removing the 3x-ETF trend-day trades. Long side (TQQQ/UPRO) and short side (SQQQ/SPXU) separately, each against random entries.
- [ ] **Extreme-band tag as turn vs continuation, split by the Flux level's slope** (extends the open 2026-11-19 Coach item): Nov 17 and 18 tags (V days) were turns; Nov 19 10:14-10:20 tags (level falling all day) were continuation (-2.3% / -3.4% more). Test whether (level now - level 30 min ago) / inner width, or the share of the session already under the level, separates the two, both sides, 30-session archive plus the daily archive.
- [ ] **Exit on a trend day: fixed 5% target vs a trail on 3x inverse entries.** Nov 19 orb_plain SQQQ 10:13 hit +4.95% after 22 minutes; the same entry held to 15:58 is +11.9% (leg +15.1%). One day; test the target vs eod vs a 1%-underlying giveback trail on the entries each comparator desk already takes, split by day shape (LESSON 35 says the best exit flips with the day).

