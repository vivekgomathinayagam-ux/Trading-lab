# Trading Floor day-trade lab

Run 2026-11-04T01:29+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-03, 24 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 17 | 29.4% | 0.56% | -0.59% | -0.251% | 0.4 | -4.24% | -3.98% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 17 | 35.3% | 0.7% | -0.42% | -0.024% | 0.91 | -0.46% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 24 | 45.8% | 0.84% | -0.71% | -0.001% | 1.0 | -0.19% | -3.27% | 0 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 17 | 41.2% | 0.66% | -0.29% | 0.099% | 1.57 | 1.65% | -2.09% | 0 | promising, keep collecting |
| CVD turn 3-min (SPY) | yes | 24 | 50.0% | 0.1% | -0.1% | 0.003% | 1.06 | 0.07% | -0.63% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 24 | 62.5% | 0.78% | -0.33% | 0.363% | 3.98 | 9.0% | -2.15% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 24 | 29.2% | 1.31% | -0.75% | -0.15% | 0.72 | -3.78% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 20 | 35.0% | 1.29% | -0.56% | 0.086% | 1.23 | 1.51% | -5.78% | 1 | promising, keep collecting |
| Volume spike (2x) | compare | 24 | 45.8% | 0.91% | -0.97% | -0.106% | 0.8 | -2.69% | -4.58% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -1.30%, QQQ -7.71%, TQQQ -23.29%, UPRO -5.08%, SQQQ +25.61%, SPXU +4.74%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 17 | -0.368% | -6.14% |
| EMA 9/21 + volume | 17 | -0.184% | -3.15% |
| Volume spike | 24 | -0.165% | -4.06% |
| EMA 9/21 + volume v2 | 17 | -0.048% | -0.86% |
| CVD turn 3-min (SPY) | 24 | -0.059% | -1.41% |
| CVD turn 3-min (TQQQ) | 24 | 0.168% | 4.03% |
| ORB (no volume filter) | 24 | -0.269% | -6.5% |
| EMA 9/21 (no volume filter) | 20 | -0.049% | -1.17% |
| Volume spike (2x) | 24 | -0.272% | -6.5% |

## Robustness check: 5-minute bars, 2026-09-11 to 2026-11-03 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 21 | 38.1% | -0.286% | 0.45 | -5.93% | -9.48% |
| EMA 9/21 + volume | 17 | 41.2% | -0.129% | 0.35 | -2.19% | -2.42% |
| Volume spike | 35 | 40.0% | -0.34% | 0.39 | -11.42% | -14.35% |
| EMA 9/21 + volume v2 | 17 | 41.2% | -0.129% | 0.35 | -2.19% | -2.42% |
| CVD turn 3-min (SPY) | 38 | 52.6% | -0.009% | 0.81 | -0.33% | -0.65% |
| CVD turn 3-min (TQQQ) | 38 | 50.0% | -0.107% | 0.68 | -4.11% | -5.17% |
| ORB (no volume filter) | 38 | 39.5% | -0.129% | 0.72 | -5.07% | -7.03% |
| EMA 9/21 (no volume filter) | 33 | 42.4% | 0.094% | 1.28 | 2.88% | -5.71% |
| Volume spike (2x) | 38 | 39.5% | -0.261% | 0.51 | -9.67% | -10.85% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4196 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4196 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4196 | 6.67% | 30.93% | 1.48% | 3.77% |
| UPRO | 4196 | 3.22% | 21.33% | 0.71% | 1.84% |
| SQQQ | 4196 | 9.96% | 28.88% | 1.53% | 5.0% |
| SPXU | 4196 | 5.7% | 18.76% | 0.69% | 2.76% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-1.54; SPXU 4 trades, $-18.49; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 2 trades, $-25.38 · exits {'eod': 16, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 3 trades, $-1.92; SPXU 9 trades, $+10.91; SPY 2 trades, $+1.64; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 17}
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 9 trades, $+29.85; SPY 1 trades, $-1.58; SQQQ 1 trades, $-16.43; UPRO 7 trades, $-25.83 · exits {'eod': 22, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 4 trades, $-5.13; SPXU 6 trades, $+30.06; SPY 2 trades, $+1.64; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 17}
- **CVD turn 3-min (SPY):** SPY 24 trades, $+0.68 · exits {'cvd_sell': 24}
- **CVD turn 3-min (TQQQ):** TQQQ 24 trades, $+90.03 · exits {'cvd_sell': 24}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
