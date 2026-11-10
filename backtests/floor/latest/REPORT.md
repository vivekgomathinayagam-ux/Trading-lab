# Trading Floor day-trade lab

Run 2026-11-10T03:39+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-09, 28 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 19 | 31.6% | 1.29% | -0.7% | -0.074% | 0.85 | -1.59% | -3.54% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 20 | 30.0% | 0.68% | -0.44% | -0.107% | 0.66 | -2.18% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 28 | 50.0% | 0.94% | -0.72% | 0.112% | 1.31 | 2.98% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 19 | 36.8% | 0.64% | -0.35% | 0.017% | 1.08 | 0.27% | -2.37% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 28 | 39.3% | 0.14% | -0.2% | -0.067% | 0.45 | -1.87% | -2.07% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 28 | 57.1% | 0.78% | -0.37% | 0.285% | 2.78 | 8.2% | -2.97% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 28 | 32.1% | 1.64% | -0.71% | 0.046% | 1.1 | 0.92% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 23 | 30.4% | 1.29% | -0.68% | -0.082% | 0.83 | -2.11% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 28 | 50.0% | 1.34% | -0.97% | 0.186% | 1.38 | 4.97% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -1.54%, QQQ -8.59%, TQQQ -27.00%, UPRO -6.76%, SQQQ +25.65%, SPXU +4.11%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 19 | -0.214% | -4.19% |
| EMA 9/21 + volume | 20 | -0.278% | -5.47% |
| Volume spike | 28 | -0.052% | -1.65% |
| EMA 9/21 + volume v2 | 19 | -0.15% | -2.86% |
| CVD turn 3-min (SPY) | 28 | -0.129% | -3.56% |
| CVD turn 3-min (TQQQ) | 28 | 0.1% | 2.75% |
| ORB (no volume filter) | 28 | -0.068% | -2.24% |
| EMA 9/21 (no volume filter) | 23 | -0.208% | -4.9% |
| Volume spike (2x) | 28 | 0.026% | 0.39% |

## Robustness check: 5-minute bars, 2026-09-17 to 2026-11-09 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 31.6% | -0.338% | 0.54 | -6.46% | -11.58% |
| EMA 9/21 + volume | 13 | 46.2% | -0.089% | 0.49 | -1.16% | -1.99% |
| Volume spike | 35 | 31.4% | -0.272% | 0.53 | -9.36% | -16.32% |
| EMA 9/21 + volume v2 | 13 | 46.2% | -0.089% | 0.49 | -1.16% | -1.99% |
| CVD turn 3-min (SPY) | 38 | 52.6% | -0.02% | 0.68 | -0.75% | -1.21% |
| CVD turn 3-min (TQQQ) | 38 | 52.6% | -0.099% | 0.72 | -3.82% | -5.39% |
| ORB (no volume filter) | 38 | 39.5% | -0.018% | 0.96 | -1.07% | -7.02% |
| EMA 9/21 (no volume filter) | 32 | 37.5% | -0.074% | 0.83 | -2.63% | -5.64% |
| Volume spike (2x) | 38 | 36.8% | -0.245% | 0.56 | -9.17% | -16.72% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4201 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4201 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4201 | 6.71% | 30.92% | 1.48% | 3.78% |
| UPRO | 4201 | 3.24% | 21.33% | 0.71% | 1.83% |
| SQQQ | 4201 | 9.97% | 28.92% | 1.52% | 5.02% |
| SPXU | 4201 | 5.71% | 18.81% | 0.69% | 2.79% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 3 trades, $-1.04; SPXU 4 trades, $-18.63; SPY 4 trades, $-1.85; SQQQ 2 trades, $+68.75; TQQQ 1 trades, $-9.44; UPRO 5 trades, $-53.62 · exits {'eod': 17, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 3 trades, $-12.16; SPXU 11 trades, $+4.78; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 3 trades, $-17.31 · exits {'eod': 20}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+52.73; SPY 2 trades, $+0.62; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 10 trades, $-25.97 · exits {'eod': 26, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 3 trades, $-12.16; SPXU 8 trades, $+23.88; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 2 trades, $-12.66 · exits {'eod': 19}
- **CVD turn 3-min (SPY):** SPY 28 trades, $-18.69 · exits {'cvd_sell': 27, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 28 trades, $+82.00 · exits {'cvd_sell': 27, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
