# Trading Floor day-trade lab

Run 2026-11-13T01:57+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-12, 31 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 22 | 27.3% | 0.47% | -0.7% | -0.378% | 0.25 | -8.08% | -7.82% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 23 | 34.8% | 0.56% | -0.5% | -0.134% | 0.59 | -3.11% | -3.7% | 0 | loses or too thin after costs |
| Volume spike | yes | 31 | 41.9% | 0.92% | -0.57% | 0.052% | 1.16 | 1.43% | -3.27% | 0 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 23 | 39.1% | 0.54% | -0.43% | -0.051% | 0.8 | -1.24% | -2.93% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 31 | 51.6% | 0.12% | -0.21% | -0.04% | 0.6 | -1.25% | -1.97% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 31 | 54.8% | 0.74% | -0.62% | 0.125% | 1.44 | 3.79% | -5.17% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 31 | 29.0% | 1.64% | -0.74% | -0.049% | 0.91 | -1.91% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 26 | 30.8% | 1.23% | -0.65% | -0.074% | 0.84 | -2.16% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 31 | 45.2% | 1.26% | -0.79% | 0.132% | 1.3 | 3.84% | -5.22% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -0.94%, QQQ -7.33%, TQQQ -24.11%, UPRO -5.20%, SQQQ +20.23%, SPXU +2.29%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 22 | -0.507% | -10.66% |
| EMA 9/21 + volume | 23 | -0.289% | -6.52% |
| Volume spike | 31 | -0.103% | -3.32% |
| EMA 9/21 + volume v2 | 23 | -0.185% | -4.23% |
| CVD turn 3-min (SPY) | 31 | -0.101% | -3.12% |
| CVD turn 3-min (TQQQ) | 31 | -0.063% | -2.07% |
| ORB (no volume filter) | 31 | -0.158% | -5.18% |
| EMA 9/21 (no volume filter) | 26 | -0.199% | -5.28% |
| Volume spike (2x) | 31 | -0.026% | -1.14% |

## Robustness check: 5-minute bars, 2026-09-18 to 2026-11-12 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 22 | 36.4% | -0.102% | 0.82 | -2.48% | -9.54% |
| EMA 9/21 + volume | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| Volume spike | 37 | 43.2% | -0.111% | 0.77 | -4.33% | -14.03% |
| EMA 9/21 + volume v2 | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| CVD turn 3-min (SPY) | 40 | 55.0% | -0.025% | 0.63 | -1.02% | -1.35% |
| CVD turn 3-min (TQQQ) | 40 | 52.5% | -0.129% | 0.64 | -5.17% | -5.63% |
| ORB (no volume filter) | 40 | 37.5% | -0.057% | 0.88 | -2.68% | -6.98% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.053% | 0.88 | -2.07% | -5.66% |
| Volume spike (2x) | 40 | 35.0% | -0.215% | 0.63 | -8.58% | -12.24% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4203 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4203 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4203 | 6.71% | 30.91% | 1.48% | 3.78% |
| UPRO | 4203 | 3.24% | 21.32% | 0.71% | 1.83% |
| SQQQ | 4203 | 9.97% | 28.96% | 1.52% | 5.02% |
| SPXU | 4203 | 5.71% | 18.8% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 5 trades, $-1.32; SPXU 5 trades, $-32.03; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 2 trades, $-11.99; UPRO 4 trades, $-47.88 · exits {'eod': 21, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 6 trades, $-16.57; SPXU 10 trades, $+12.31; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 3 trades, $-28.77 · exits {'eod': 23}
- **Volume spike:** QQQ 7 trades, $+11.68; SPXU 10 trades, $+54.08; SPY 4 trades, $-6.10; SQQQ 1 trades, $-16.43; UPRO 9 trades, $-28.94 · exits {'eod': 29, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-19.78; SPXU 7 trades, $+31.46; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-26.74 · exits {'eod': 23}
- **CVD turn 3-min (SPY):** SPY 31 trades, $-12.51 · exits {'cvd_sell': 30, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 31 trades, $+37.90 · exits {'cvd_sell': 29, 'stop': 2}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
