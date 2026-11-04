# IDEA BACKLOG (the Researcher picks; nobody needs to ask Vivek)

Rank by: expected edge × testability with our data ÷ cost.
- Every idea gets a long and a short side.
- Tick an idea off with a link to its result. Add new ideas freely.

## Levels a discretionary trader watches (Vivek's chart shows these)
- [ ] Pre-market high/low break and retest (needs pre-market bars; Yahoo has them with includePrePost)
- [ ] Prior-day high/low/close: break-and-hold vs reject
- [ ] Opening drive: first 5/15/30 min direction continuation vs reversal, split by gap size
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
- [ ] Prior-day high/low break: next on the list (chartable; no history problem; both sides)
- [ ] volspike-only giveback trail (`volspike_gb`): +0.18% per trade over 24 backtest entries; picked after the fact, so a lead only. Test only on sessions after Nov 4

## Data upgrades
- [ ] Long history: Alpaca free minute bars since 2016 (needs Vivek's free key as a GitHub Actions secret)
