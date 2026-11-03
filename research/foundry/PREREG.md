# Foundry batch 1: trend-ride, VWAP, reversal-break and Fibonacci rules (pre-registered)

Written 2026-11-03 12:40 PT, **before any result was computed**. Trigger: Vivek's Nov 3 review. SPY trended up from about 751 to 757 and then broke down to about 753.7. Five paper desks went long, but none captured the move: the CVD desks' exits fired after 3 minutes, and the other desks hold to 15:55 with no trailing exit. There is also no rule that goes short on a breakdown.

## Question
Do simple, chartable trend and level rules make money on SPY and QQQ intraday after costs, out of sample?
The rules come from what a discretionary trader reads off a 5-minute chart: Ripster EMA clouds, VWAP, a trend break, and Fibonacci pullbacks.

## Data
- 1-minute bars from the archive on branch `data` (`backtests/data/etf1m`). Regular hours only, Sep 28 to Nov 2, 2026, which is 26 sessions.
- The bars are resampled to 5 minutes by clock buckets.
- The same code also runs in GitHub Actions on Yahoo 5-minute bars for about 60 sessions (the second sample).
- Nov 3 itself is held out as a one-day check and is not used for any choice.

## Shared mechanics
- Decisions are made at a 5-minute bar's close and filled at the next bar's open. A stop fills at the stop level, or at the bar's open if it gaps through.
- Flat by 15:55 ET. No entries before 09:45 ET or after 15:30 ET.
- Long and short both run on the ETF itself. Live, a short would have to be a put spread or an inverse ETF; this batch only measures the edge.
- Costs: 0.02% slippage per side plus a 0.003% fee per side.
- Results are reported as % move per trade, net of costs, plus a 3x-leveraged equivalent (×3, ignoring decay).
- At most 3 trades per rule per symbol per day, one position at a time.

## Rules (fixed now)
| Id | Entry | Exit |
|---|---|---|
| F1 `cloud_ride` | Ripster clouds on 5-min closes: fast = EMA5/EMA12, slow = EMA34/EMA50. Long when the fast cloud is fully above the slow cloud, the bar's low touched the fast cloud, and the bar closed above EMA12. Short is the mirror. | 5-min close beyond the far side of the slow cloud (long: below min(EMA34, EMA50)), or a hard stop of 0.5%, or 15:55 |
| F2 `cloud_ride_tight` | same as F1 | 5-min close beyond the fast cloud (long: below min(EMA5, EMA12)), or a hard stop of 0.5%, or 15:55 |
| F3 `vwap_trend` | From 10:00. Long on the first 5-min close above session VWAP while EMA9 > EMA21 (5-min). Short is the mirror. | 5-min close back across VWAP, or a hard stop of 0.5%, or 15:55 |
| F4 `trend_break` | Short on the first 5-min close below VWAP after at least 12 straight 5-min closes above it. Long is the mirror. | Stop at the highest high of the last 6 bars before entry (long: lowest low); otherwise 15:55 |
| F5 `fib_618` | From 10:30, once the session range is at least 0.4%. Uptrend = session high made after session low and last close above VWAP. Long when a bar's low reaches the 50-61.8% retracement of low→high and the bar closes above the 50% level. Downtrend is the mirror (short). One trade per direction per day. | Stop on a 5-min close beyond the 78.6% level; target is the session extreme as of entry; otherwise 15:55 |
| F6 `fib_382` | Same as F5, but the zone is 38.2-50% and the stop is a close beyond 61.8% | same as F5 |

Controls:
- C1: long at the 09:45 open, out at 15:55.
- C2: random entries, same count and direction mix as each rule, held for the same number of bars (500 draws).

## Success bar (all must hold for "promising")
1. Net expectancy > 0 on the 26-session sample, with day-block bootstrap 95% CI lower bound > −0.02%.
2. Positive in both halves (sessions 1-13 and 14-26), separately for SPY and QQQ pooled per half.
3. Beats the C2 random control (rule mean above the 95th percentile of random means).
4. Positive on the independent 60-session 5-minute sample, where it overlaps less.
5. Survives 2x costs.

Anything that passes becomes a paper desk (a new key; existing desks untouched) and is judged forward.
Anything that fails is logged with its numbers in `research/LESSONS.md`.
Variants in this batch: 6 rules + 2 controls = 8 (running total 146).
