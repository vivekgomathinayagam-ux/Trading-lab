# Trading Floor day-trade lab

Run 2026-10-30T01:09+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-29, 21 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 15 | 33.3% | 0.66% | -0.61% | -0.186% | 0.54 | -2.82% | -3.04% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 15 | 33.3% | 0.29% | -0.44% | -0.194% | 0.33 | -2.89% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 21 | 47.6% | 0.83% | -0.6% | 0.082% | 1.26 | 1.61% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 15 | 40.0% | 0.32% | -0.3% | -0.052% | 0.71 | -0.78% | -2.09% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 21 | 57.1% | 0.1% | -0.12% | 0.01% | 1.19 | 0.2% | -0.63% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 21 | 61.9% | 0.75% | -0.31% | 0.348% | 3.91 | 7.5% | -2.15% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 21 | 33.3% | 1.31% | -0.8% | -0.097% | 0.82 | -2.25% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 18 | 33.3% | 0.7% | -0.61% | -0.171% | 0.58 | -3.12% | -5.78% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 21 | 47.6% | 0.91% | -0.9% | -0.036% | 0.92 | -0.91% | -3.26% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY +0.68%, QQQ -3.68%, TQQQ -12.24%, UPRO +0.96%, SQQQ +11.13%, SPXU -1.24%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 15 | -0.318% | -4.73% |
| EMA 9/21 + volume | 15 | -0.356% | -5.23% |
| Volume spike | 21 | -0.101% | -2.25% |
| EMA 9/21 + volume v2 | 15 | -0.205% | -3.04% |
| CVD turn 3-min (SPY) | 21 | -0.052% | -1.1% |
| CVD turn 3-min (TQQQ) | 21 | 0.154% | 3.22% |
| ORB (no volume filter) | 21 | -0.217% | -4.69% |
| EMA 9/21 (no volume filter) | 18 | -0.306% | -5.46% |
| Volume spike (2x) | 21 | -0.199% | -4.25% |

## Robustness check: 5-minute bars, 2026-09-04 to 2026-10-29 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 22 | 45.5% | -0.235% | 0.41 | -5.11% | -7.32% |
| EMA 9/21 + volume | 16 | 43.8% | -0.131% | 0.36 | -2.08% | -2.32% |
| Volume spike | 36 | 38.9% | -0.353% | 0.27 | -12.04% | -12.31% |
| EMA 9/21 + volume v2 | 16 | 43.8% | -0.131% | 0.36 | -2.08% | -2.32% |
| CVD turn 3-min (SPY) | 39 | 56.4% | -0.007% | 0.86 | -0.27% | -0.73% |
| CVD turn 3-min (TQQQ) | 39 | 48.7% | -0.073% | 0.73 | -2.9% | -5.45% |
| ORB (no volume filter) | 39 | 41.0% | -0.094% | 0.78 | -3.87% | -7.06% |
| EMA 9/21 (no volume filter) | 35 | 37.1% | -0.075% | 0.78 | -2.74% | -5.71% |
| Volume spike (2x) | 39 | 43.6% | -0.17% | 0.61 | -6.61% | -7.61% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4193 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4193 | 0.19% | 3.63% | 0.07% | 0.1% |
| TQQQ | 4193 | 6.68% | 30.91% | 1.48% | 3.77% |
| UPRO | 4193 | 3.22% | 21.3% | 0.72% | 1.84% |
| SQQQ | 4193 | 9.92% | 28.91% | 1.53% | 4.98% |
| SPXU | 4193 | 5.7% | 18.77% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $-1.73; SPXU 4 trades, $-18.49; SPY 4 trades, $-1.88; SQQQ 1 trades, $+21.67; TQQQ 2 trades, $-2.33; UPRO 2 trades, $-25.38 · exits {'eod': 14, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 2 trades, $-0.21; SPXU 8 trades, $-15.66; SPY 2 trades, $+2.20; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 15}
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 8 trades, $+20.63; SQQQ 1 trades, $-16.43; UPRO 6 trades, $-0.13 · exits {'eod': 20, 'stop': 1}
- **EMA 9/21 + volume v2:** QQQ 3 trades, $-3.42; SPXU 5 trades, $+3.49; SPY 2 trades, $+2.20; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 15}
- **CVD turn 3-min (SPY):** SPY 21 trades, $+1.99 · exits {'cvd_sell': 21}
- **CVD turn 3-min (TQQQ):** TQQQ 21 trades, $+74.95 · exits {'cvd_sell': 21}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
