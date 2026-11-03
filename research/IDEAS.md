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
- [ ] Trend-day detector by 10:30 ET (range expansion + VWAP slope) → only run trend rules on trend days
- [ ] Day-of-week and event days (CPI, FOMC) splits
- [ ] VIX level / term structure as a gate (Tempest)

## Options-native (needs real option prices; Skylit has 30 days intraday)
- [ ] 1-day iron condor at ±1 priced sigma (variance premium, queued)
- [ ] 0DTE debit spread on cloud-ride signals vs trading the ETF (does the option leverage survive the spread?)

## Data upgrades
- [ ] Long history: Alpaca free minute bars since 2016 (needs Vivek's free key as a GitHub Actions secret)
