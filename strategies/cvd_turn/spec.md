# CVD turn, 3-minute candles (pre-registered 2026-10-28, before any test)

Vivek's setup: buy when CVD rises from its 5-candle low, sell when it falls from its 5-candle high; skip fast
spikes; regular hours only. The Researcher fixed every definition below **before** running anything.
Changing any of it later is a new desk key (`cvd_spy_v2`, ...), never an edit.

## Hypothesis
Cumulative volume delta (buying vs selling pressure) turning up from a short-term low marks the end of a
selling push; price follows for the next minutes to hours. The turn back down marks the end of the buying
push and is the exit.

## Data and how CVD is approximated
No tick data exists (Yahoo/Tradier give 1-minute OHLCV only). Volume delta per 1-minute bar is approximated
with the close-location value: `delta = volume x ((close - low) - (high - close)) / (high - low)`, 0 when
high == low. A bar closing at its high counts all its volume as buying; at its low, all selling.
This is an approximation; true CVD needs trade-by-trade bid/ask data. If the setup works on the
approximation, a version on real delta (Skylit flow or a tick feed) is the next step.

- 3-minute candles by clock from 09:30 ET: 09:30-09:32, 09:33-09:35, ... A candle closes on its third
  minute's bar; if that bar is missing, it closes when the first bar of a later candle arrives.
- Candle delta = sum of its bars' deltas. CVD = running sum of candle deltas, reset at 09:30 each session.

## Signals (decided at a 3-minute candle close k, no look-ahead)
- **Buy turn:** candle k-1 holds the lowest CVD of candles k-5..k-1, and CVD[k] > CVD[k-1].
- **Sell turn:** candle k-1 holds the highest CVD of candles k-5..k-1, and CVD[k] < CVD[k-1].
- Needs 5 complete candles of today's session before candle k (first possible signal 09:47:59 ET).
- **Skip fast spikes (entries only):** no entry when candle k's range (high - low) is more than 3x the median
  range of today's earlier candles (at least 5 of them). Exits are never skipped.

## Desks (two, each counts as a variant)
| Desk | Signal from | Buys |
|---|---|---|
| `cvd_spy` | SPY's own CVD | SPY (Vivek's spec instrument) |
| `cvd_tqqq` | TQQQ's own CVD | TQQQ (3x Nasdaq; Vivek's focus on leveraged ETFs) |

## Entry, exit, sizing, costs (shared day-trade machinery, `strategies/daytrade/spec.md`)
- Entry: buy at the next 1-minute bar's open after a buy turn. New entries 09:35-15:30 ET. Long only.
- Exit, first of: **sell turn** (next 1-minute bar's open), stop -2.5%, target +5%, flat 15:55 ET.
- One entry per desk per day (cash-account settlement). All desk cash, whole shares, no margin. $1,000 book.
- Costs: slippage 0.02% per side SPY, 0.05% TQQQ. Stress at 2x and 3x.
- Holding time: minutes to hours, never overnight.

## Test plan
- One backtest on the archived 1-minute bars (2026-09-28 onward, ~22 sessions, 3-session warm-up), 1x / 2x / 3x
  costs. No parameters are tuned; the numbers above are the only ones run.
- Then paper from the next session regardless of the result (Vivek's setup).
- Honest limit: about 19 sessions means at most 19 trades per desk in the backtest. No verdict is possible
  from that alone.

## What would prove it wrong
After 30+ paper trades per desk: expectancy after costs <= 0, or the bootstrap 95% CI of expectancy entirely
below zero at any point after 15 trades, or results no better than buying the same ETF at 09:48 and
selling at 15:55 on the same days (the "just be long" control computed in the weekly report).
