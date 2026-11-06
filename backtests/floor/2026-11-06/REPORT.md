# Trading Floor day-trade lab

Run 2026-11-06T01:39+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-05, 26 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 18 | 27.8% | 0.56% | -0.59% | -0.272% | 0.37 | -4.84% | -4.58% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 19 | 31.6% | 0.7% | -0.44% | -0.076% | 0.74 | -1.51% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 26 | 46.2% | 0.97% | -0.67% | 0.088% | 1.24 | 2.1% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 19 | 36.8% | 0.66% | -0.33% | 0.034% | 1.16 | 0.6% | -2.09% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 26 | 50.0% | 0.1% | -0.24% | -0.068% | 0.43 | -1.77% | -1.97% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 26 | 61.5% | 0.75% | -0.54% | 0.253% | 2.22 | 6.68% | -2.47% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 26 | 30.8% | 1.75% | -0.72% | 0.038% | 1.08 | 0.64% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 22 | 31.8% | 1.29% | -0.69% | -0.058% | 0.88 | -1.52% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 26 | 46.2% | 1.24% | -0.95% | 0.062% | 1.12 | 1.31% | -5.22% | 1 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -4.09%, QQQ -12.76%, TQQQ -36.00%, UPRO -13.45%, SQQQ +45.29%, SPXU +12.81%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 18 | -0.393% | -6.91% |
| EMA 9/21 + volume | 19 | -0.228% | -4.3% |
| Volume spike | 26 | -0.079% | -2.22% |
| EMA 9/21 + volume v2 | 19 | -0.104% | -2.01% |
| CVD turn 3-min (SPY) | 26 | -0.13% | -3.34% |
| CVD turn 3-min (TQQQ) | 26 | 0.062% | 1.52% |
| ORB (no volume filter) | 26 | -0.08% | -2.42% |
| EMA 9/21 (no volume filter) | 22 | -0.186% | -4.25% |
| Volume spike (2x) | 26 | -0.103% | -2.94% |

## Robustness check: 5-minute bars, 2026-09-11 to 2026-11-05 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 22 | 40.9% | -0.077% | 0.85 | -1.92% | -9.48% |
| EMA 9/21 + volume | 18 | 44.4% | -0.231% | 0.25 | -4.1% | -4.33% |
| Volume spike | 37 | 43.2% | -0.202% | 0.63 | -7.5% | -14.35% |
| EMA 9/21 + volume v2 | 18 | 44.4% | -0.231% | 0.25 | -4.1% | -4.33% |
| CVD turn 3-min (SPY) | 40 | 50.0% | -0.036% | 0.5 | -1.42% | -1.35% |
| CVD turn 3-min (TQQQ) | 40 | 47.5% | -0.165% | 0.57 | -6.53% | -6.23% |
| ORB (no volume filter) | 40 | 40.0% | -0.019% | 0.96 | -1.15% | -7.03% |
| EMA 9/21 (no volume filter) | 35 | 40.0% | 0.004% | 1.01 | -0.15% | -5.71% |
| Volume spike (2x) | 40 | 40.0% | -0.167% | 0.69 | -6.8% | -12.25% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4198 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4198 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4198 | 6.69% | 30.92% | 1.48% | 3.76% |
| UPRO | 4198 | 3.22% | 21.32% | 0.71% | 1.83% |
| SQQQ | 4198 | 9.96% | 28.89% | 1.52% | 5.0% |
| SPXU | 4198 | 5.69% | 18.77% | 0.69% | 2.76% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-1.54; SPXU 4 trades, $-18.49; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 3 trades, $-31.36 · exits {'eod': 17, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-12.37; SPXU 9 trades, $+10.91; SPY 2 trades, $+1.64; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 19}
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 10 trades, $+54.08; SPY 1 trades, $-1.58; SQQQ 1 trades, $-16.43; UPRO 8 trades, $-27.07 · exits {'eod': 24, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 6 trades, $-15.58; SPXU 6 trades, $+30.06; SPY 2 trades, $+1.64; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 19}
- **CVD turn 3-min (SPY):** SPY 26 trades, $-17.73 · exits {'cvd_sell': 25, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 26 trades, $+66.79 · exits {'cvd_sell': 25, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
