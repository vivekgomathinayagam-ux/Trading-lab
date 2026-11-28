# Trading Floor day-trade lab

Run 2026-11-28T02:14+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-27, 41 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 22 | 22.7% | 1.77% | -0.77% | -0.195% | 0.67 | -4.44% | -5.65% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 27 | 37.0% | 0.74% | -0.53% | -0.061% | 0.82 | -1.74% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 41 | 46.3% | 1.42% | -0.8% | 0.228% | 1.53 | 9.21% | -4.94% | 2 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 25 | 40.0% | 0.69% | -0.46% | -0.003% | 0.99 | -0.16% | -3.58% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 41 | 34.1% | 1.91% | -0.8% | 0.127% | 1.24 | 4.68% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 33 | 33.3% | 1.46% | -0.69% | 0.03% | 1.07 | 0.58% | -5.78% | 2 | loses or too thin after costs |
| Volume spike (2x) | compare | 41 | 51.2% | 1.71% | -1.07% | 0.353% | 1.67 | 14.65% | -4.52% | 4 | promising, keep collecting |

Buy-and-hold over the same window: SPY -4.72%, QQQ -12.33%, TQQQ -38.07%, UPRO -17.15%, SQQQ +34.39%, SPXU +12.15%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 22 | -0.353% | -7.71% |
| EMA 9/21 + volume | 27 | -0.225% | -5.99% |
| Volume spike | 41 | 0.067% | 2.26% |
| EMA 9/21 + volume v2 | 25 | -0.169% | -4.22% |
| ORB (no volume filter) | 41 | 0.015% | -0.03% |
| EMA 9/21 (no volume filter) | 33 | -0.086% | -3.19% |
| Volume spike (2x) | 41 | 0.187% | 7.14% |

## Robustness check: 5-minute bars, 2026-10-05 to 2026-11-27 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 13 | 46.2% | 0.192% | 1.38 | 2.3% | -5.5% |
| EMA 9/21 + volume | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| Volume spike | 32 | 53.1% | 0.27% | 1.81 | 8.65% | -8.56% |
| EMA 9/21 + volume v2 | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| ORB (no volume filter) | 39 | 33.3% | 0.153% | 1.27 | 5.38% | -5.64% |
| EMA 9/21 (no volume filter) | 31 | 35.5% | 0.054% | 1.12 | 1.29% | -5.7% |
| Volume spike (2x) | 38 | 42.1% | 0.094% | 1.2 | 3.14% | -10.19% |

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

- **ORB + volume:** QQQ 3 trades, $-5.41; SPXU 6 trades, $-41.29; SPY 3 trades, $+0.71; SQQQ 3 trades, $+84.28; UPRO 7 trades, $-82.63 · exits {'eod': 19, 'stop': 2, 'target': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-4.77; SPXU 12 trades, $+6.33; SPY 3 trades, $+10.25; SQQQ 2 trades, $+13.86; TQQQ 1 trades, $-0.79; UPRO 8 trades, $-42.24 · exits {'eod': 27}
- **Volume spike:** QQQ 4 trades, $-0.92; SPXU 12 trades, $+78.73; SPY 5 trades, $+16.64; SQQQ 6 trades, $+25.41; TQQQ 1 trades, $+13.15; UPRO 13 trades, $-40.87 · exits {'eod': 35, 'stop': 4, 'target': 2}
- **EMA 9/21 + volume v2:** QQQ 1 trades, $-4.77; SPXU 9 trades, $+25.33; SPY 3 trades, $+10.25; SQQQ 5 trades, $+14.66; TQQQ 1 trades, $-0.85; UPRO 6 trades, $-46.19 · exits {'eod': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
