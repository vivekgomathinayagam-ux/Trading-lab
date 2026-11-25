# Trading Floor day-trade lab

Run 2026-11-25T23:54+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-25, 40 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 22 | 22.7% | 1.77% | -0.77% | -0.194% | 0.68 | -4.41% | -5.65% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 27 | 37.0% | 0.74% | -0.53% | -0.06% | 0.82 | -1.71% | -4.17% | 0 | loses or too thin after costs |
| Volume spike | yes | 40 | 45.0% | 1.5% | -0.8% | 0.234% | 1.53 | 9.23% | -4.94% | 2 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 25 | 40.0% | 0.69% | -0.46% | -0.003% | 0.99 | -0.16% | -3.58% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 40 | 35.0% | 1.91% | -0.73% | 0.192% | 1.4 | 7.31% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 33 | 33.3% | 1.46% | -0.69% | 0.03% | 1.07 | 0.58% | -5.78% | 2 | loses or too thin after costs |
| Volume spike (2x) | compare | 40 | 52.5% | 1.71% | -1.0% | 0.425% | 1.9 | 17.65% | -4.5% | 4 | promising, keep collecting |

Buy-and-hold over the same window: SPY -6.23%, QQQ -14.65%, TQQQ -42.65%, UPRO -21.03%, SQQQ +45.76%, SPXU +18.08%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 22 | -0.352% | -7.68% |
| EMA 9/21 + volume | 27 | -0.224% | -5.97% |
| Volume spike | 40 | 0.071% | 2.33% |
| EMA 9/21 + volume v2 | 25 | -0.169% | -4.22% |
| ORB (no volume filter) | 40 | 0.079% | 2.57% |
| EMA 9/21 (no volume filter) | 33 | -0.086% | -3.19% |
| Volume spike (2x) | 40 | 0.258% | 10.04% |

## Robustness check: 5-minute bars, 2026-10-01 to 2026-11-25 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 14 | 35.7% | 0.01% | 1.02 | -0.08% | -6.32% |
| EMA 9/21 + volume | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| Volume spike | 33 | 48.5% | 0.15% | 1.36 | 4.69% | -10.28% |
| EMA 9/21 + volume v2 | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| ORB (no volume filter) | 40 | 32.5% | 0.182% | 1.34 | 6.79% | -5.76% |
| EMA 9/21 (no volume filter) | 33 | 36.4% | 0.036% | 1.08 | 0.79% | -5.72% |
| Volume spike (2x) | 39 | 38.5% | -0.009% | 0.98 | -0.83% | -10.41% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4213 | 0.17% | 1.73% | 0.05% | 0.02% |
| QQQ | 4213 | 0.19% | 3.68% | 0.07% | 0.09% |
| TQQQ | 4213 | 6.74% | 31.05% | 1.5% | 3.8% |
| UPRO | 4213 | 3.25% | 21.46% | 0.74% | 1.85% |
| SQQQ | 4213 | 10.06% | 28.93% | 1.52% | 5.06% |
| SPXU | 4213 | 5.77% | 18.8% | 0.69% | 2.82% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 3 trades, $-5.41; SPXU 6 trades, $-41.29; SPY 3 trades, $+0.71; SQQQ 3 trades, $+84.28; UPRO 7 trades, $-82.39 · exits {'eod': 19, 'stop': 2, 'target': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-4.77; SPXU 12 trades, $+6.33; SPY 3 trades, $+10.25; SQQQ 2 trades, $+13.86; TQQQ 1 trades, $-0.79; UPRO 8 trades, $-42.00 · exits {'eod': 27}
- **Volume spike:** QQQ 3 trades, $-0.99; SPXU 12 trades, $+78.73; SPY 5 trades, $+16.64; SQQQ 6 trades, $+25.41; TQQQ 1 trades, $+13.15; UPRO 13 trades, $-40.63 · exits {'eod': 34, 'stop': 4, 'target': 2}
- **EMA 9/21 + volume v2:** QQQ 1 trades, $-4.77; SPXU 9 trades, $+25.33; SPY 3 trades, $+10.25; SQQQ 5 trades, $+14.66; TQQQ 1 trades, $-0.85; UPRO 6 trades, $-46.19 · exits {'eod': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
