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
- [ ] Condor v2: short strikes where the credit is ≥ 20% of the width, or a 1.5-sigma 2-5 DTE condor; size $1 wings under the 5% cap (needs a reason beyond 'try again'; credit/width is that reason)
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
- [ ] Dip-buy filter for CVD longs (mirror for CVD sells): skip a long when the index is 1% or more under its open at entry; skip a short when 1% or more over. Nov 5: both CVD longs at 10:09 were bought 1.4% under the open and lost (-2.98% stop, -1.63%). Counter: Oct 30 (SPY -0.74%) CVD longs won +1.56/+0.22%, so count qualifying days first.
- [ ] Hard stop for 3x-ETF longs (e.g. -1.5%): cvd_tqqq's stop fired at -2.98% on Nov 5. Test the stop level for the CVD desks both sides, with the stop gap risk of a fast move.
- [x] (2026-11-07 done, LESSONS 23 update) Late-entry bucket by side (extends the 2026-11-04 idea): Nov 5 ema_vol QQQ long at 14:45 into a falling tape lost -1.21%. Forward count of 13:00+ paper entries is 1 of 10.

## From the Coach, 2026-11-06 (hindsight leads only; the Researcher pre-registers)
- [x] (2026-11-07 untestable, n=2, LESSONS 29; retest on the Alpaca history) Failed opening drive, both sides: after a first-25-minute move of 0.9% or more on SPY (1.3% QQQ), trade the reverse (SQQQ/SPXU after an up-drive, TQQQ/UPRO after a down-drive) on the first close through the drive's midpoint, flat by 15:55 or at a VWAP reclaim. Nov 6: QQQ +1.43% to 09:53, then -1.58%; SQQQ +5.3% available. Count qualifying days first; most will be continuations (Nov 5 was one) so it must not be a regime bet (LESSON 24).
- [x] (2026-11-07 not supported, LESSONS 26 update) "Stale-high" long filter, mirror for shorts: skip a long when the day's high is 15+ minutes old and price is below VWAP; skip a short when the day's low is 15+ minutes old and price is above VWAP. Nov 6: three longs after the 09:53 high lost -$27.61.
- [ ] SQQQ/SPXU short exit: compare eod hold vs VWAP-reclaim exit vs 50% giveback after +1% (ema_vol SQQQ peaked +1.08%, ended +0.15%). This is a narrow retest of LESSON 20 for inverse-ETF shorts only, so cite 20 and use only sessions after Nov 6.

## From the Researcher, 2026-11-07
- [ ] ORB "first break only" (`orb_vol_v2` candidate): enter only on the first close above the opening-range high, never on a re-cross. Nov 6 UPRO 12:23 was a re-cross after 121 closes above the level. Test on the floor-lab desk replay (1-min) with both sides via SPXU/SQQQ; judge only on sessions after Nov 7 for paper. Lead from one day.
- [ ] Short-side 13:00 cutoff: late shorts lose their edge (LESSONS 23 update) while longs are flat by hour. Pre-register a short-only cutoff on new sessions only (both archives were used to find it).
- [ ] Entry quality over exits (LESSONS 30): MFE in the first 15 minutes after entry as a "fail fast" exit (exit at 15 min if open profit has never reached +0.1%), both sides, on desk entries and random entries. Different from LESSON 20 (giveback) and the ATR trail.

## From the Coach, 2026-11-09 (hindsight leads only; the Researcher pre-registers)
- [ ] CVD long exit variants, split by day direction: first CVD sell vs hold until close below VWAP vs hold until 15:55, for CVD longs; mirror for CVD shorts via SQQQ/SPXU (falling-day version). Nov 9: cvd_tqqq sold at 10:15 (+0.80%) and TQQQ ran to 15:29 (+8.75% leg); on Nov 5/6 the same early exits were the lesser loss. Report separately for days above and below the open (LESSON 24) and cite LESSON 20.

## From the Coach, 2026-11-10 (hindsight leads only; the Researcher pre-registers)
- [ ] Distance-under-high entry filter, both sides: skip a long when the index is 0.3%, 0.5% or 0.75% under its running intraday high at entry; mirror: skip an inverse-ETF/short entry when 0.3%+ above its running low. Compare against random entries on both archives (it differs from the stale-high filter, LESSONS 26, which used the age of the high). Evidence: LESSONS 33 (5 won / 11 lost, n=16, 10 sessions).
- [ ] V-reversal long: after a 1.5%+ QQQ down-leg, buy TQQQ/UPRO on the first 5-min close above VWAP (Nov 10: 12:45, +1.8% in 15 min); mirror: after a 1.5%+ up-leg, buy SQQQ/SPXU on the first close below VWAP. Count qualifying days first; different from LESSON 22 (0.6% leg, refuted) by the bigger leg.
- [ ] Inverse-ETF exit by VWAP reclaim vs eod, split by day shape (orb_vol SPXU Nov 10: +0.57% MFE, -1.60% at eod). Narrow retest of LESSON 20 for inverse ETFs (see the 2026-11-06 item); use sessions after Nov 6 for paper.

