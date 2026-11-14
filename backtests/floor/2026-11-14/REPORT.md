# Trading Floor day-trade lab

Run 2026-11-14T01:29+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-13, 32 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 22 | 31.8% | 1.11% | -0.73% | -0.148% | 0.7 | -3.42% | -4.28% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 23 | 30.4% | 0.6% | -0.51% | -0.169% | 0.52 | -3.89% | -4.45% | 0 | loses or too thin after costs |
| Volume spike | yes | 32 | 50.0% | 0.97% | -0.65% | 0.159% | 1.49 | 4.98% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 22 | 36.4% | 0.58% | -0.45% | -0.074% | 0.74 | -1.67% | -3.1% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 32 | 43.8% | 0.12% | -0.23% | -0.076% | 0.41 | -2.42% | -2.22% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 32 | 53.1% | 0.75% | -0.73% | 0.054% | 1.16 | 1.56% | -7.39% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 32 | 31.2% | 1.53% | -0.74% | -0.031% | 0.94 | -1.39% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 27 | 33.3% | 1.14% | -0.65% | -0.058% | 0.87 | -1.8% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 32 | 50.0% | 1.33% | -0.86% | 0.234% | 1.54 | 7.37% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -1.32%, QQQ -8.44%, TQQQ -26.89%, UPRO -6.37%, SQQQ +24.74%, SPXU +3.59%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 22 | -0.289% | -6.36% |
| EMA 9/21 + volume | 23 | -0.34% | -7.6% |
| Volume spike | 32 | -0.006% | -0.41% |
| EMA 9/21 + volume v2 | 22 | -0.23% | -4.99% |
| CVD turn 3-min (SPY) | 32 | -0.138% | -4.35% |
| CVD turn 3-min (TQQQ) | 32 | -0.132% | -4.31% |
| ORB (no volume filter) | 32 | -0.143% | -4.86% |
| EMA 9/21 (no volume filter) | 27 | -0.18% | -4.97% |
| Volume spike (2x) | 32 | 0.073% | 2.01% |

## Robustness check: 5-minute bars, 2026-09-21 to 2026-11-13 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 31.6% | -0.338% | 0.54 | -6.46% | -11.58% |
| EMA 9/21 + volume | 13 | 46.2% | -0.083% | 0.53 | -1.08% | -1.99% |
| Volume spike | 37 | 37.8% | -0.229% | 0.58 | -8.41% | -16.33% |
| EMA 9/21 + volume v2 | 13 | 46.2% | -0.083% | 0.53 | -1.08% | -1.99% |
| CVD turn 3-min (SPY) | 40 | 52.5% | -0.02% | 0.68 | -0.81% | -1.21% |
| CVD turn 3-min (TQQQ) | 40 | 52.5% | -0.126% | 0.66 | -5.04% | -5.64% |
| ORB (no volume filter) | 40 | 40.0% | -0.024% | 0.95 | -1.37% | -6.95% |
| EMA 9/21 (no volume filter) | 34 | 41.2% | -0.033% | 0.92 | -1.39% | -5.71% |
| Volume spike (2x) | 40 | 35.0% | -0.278% | 0.52 | -10.81% | -16.64% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4204 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4204 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4204 | 6.73% | 30.9% | 1.47% | 3.78% |
| UPRO | 4204 | 3.24% | 21.31% | 0.71% | 1.83% |
| SQQQ | 4204 | 9.97% | 28.97% | 1.52% | 5.02% |
| SPXU | 4204 | 5.71% | 18.82% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 5 trades, $-32.71; SPY 4 trades, $-1.85; SQQQ 2 trades, $+68.75; TQQQ 2 trades, $-13.92; UPRO 5 trades, $-53.62 · exits {'eod': 20, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 4 trades, $-16.36; SPXU 12 trades, $+6.13; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 4 trades, $-31.60 · exits {'eod': 23}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+57.74; SPY 4 trades, $-1.10; SQQQ 1 trades, $-16.43; TQQQ 2 trades, $+36.93; UPRO 11 trades, $-27.84 · exits {'eod': 30, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 4 trades, $-16.36; SPXU 9 trades, $+25.28; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 3 trades, $-29.33 · exits {'eod': 22}
- **CVD turn 3-min (SPY):** SPY 32 trades, $-24.16 · exits {'cvd_sell': 31, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 32 trades, $+15.63 · exits {'cvd_sell': 29, 'stop': 3}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
