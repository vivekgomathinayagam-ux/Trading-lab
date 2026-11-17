# Trading Floor day-trade lab

Run 2026-11-17T04:00+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-16, 33 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 23 | 30.4% | 0.64% | -0.7% | -0.292% | 0.4 | -6.6% | -7.82% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 23 | 34.8% | 0.56% | -0.5% | -0.134% | 0.59 | -3.11% | -3.7% | 0 | loses or too thin after costs |
| Volume spike | yes | 33 | 48.5% | 0.88% | -0.59% | 0.124% | 1.41 | 3.96% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 23 | 39.1% | 0.54% | -0.43% | -0.051% | 0.8 | -1.24% | -2.93% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 33 | 45.5% | 0.12% | -0.24% | -0.072% | 0.44 | -2.38% | -2.5% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 33 | 51.5% | 0.74% | -0.73% | 0.026% | 1.07 | 0.68% | -7.91% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 33 | 33.3% | 1.61% | -0.74% | 0.044% | 1.09 | 1.02% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 27 | 33.3% | 1.14% | -0.65% | -0.057% | 0.87 | -1.78% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 33 | 48.5% | 1.23% | -0.79% | 0.19% | 1.46 | 6.1% | -5.22% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -3.18%, QQQ -10.87%, TQQQ -32.75%, UPRO -11.71%, SQQQ +34.70%, SPXU +9.49%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 23 | -0.425% | -9.43% |
| EMA 9/21 + volume | 23 | -0.289% | -6.52% |
| Volume spike | 33 | -0.028% | -1.12% |
| EMA 9/21 + volume v2 | 23 | -0.185% | -4.23% |
| CVD turn 3-min (SPY) | 33 | -0.135% | -4.37% |
| CVD turn 3-min (TQQQ) | 33 | -0.159% | -5.27% |
| ORB (no volume filter) | 33 | -0.071% | -2.74% |
| EMA 9/21 (no volume filter) | 27 | -0.179% | -4.96% |
| Volume spike (2x) | 33 | 0.034% | 0.79% |

## Robustness check: 5-minute bars, 2026-09-24 to 2026-11-16 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 35.0% | -0.181% | 0.69 | -3.78% | -9.62% |
| EMA 9/21 + volume | 14 | 35.7% | -0.282% | 0.19 | -3.91% | -4.32% |
| Volume spike | 35 | 45.7% | -0.116% | 0.77 | -4.3% | -13.87% |
| EMA 9/21 + volume v2 | 14 | 35.7% | -0.282% | 0.19 | -3.91% | -4.32% |
| CVD turn 3-min (SPY) | 38 | 57.9% | -0.021% | 0.7 | -0.78% | -1.19% |
| CVD turn 3-min (TQQQ) | 38 | 55.3% | -0.113% | 0.7 | -4.33% | -5.62% |
| ORB (no volume filter) | 38 | 36.8% | -0.014% | 0.97 | -0.99% | -7.04% |
| EMA 9/21 (no volume filter) | 32 | 40.6% | -0.06% | 0.86 | -2.16% | -5.63% |
| Volume spike (2x) | 38 | 39.5% | -0.177% | 0.68 | -6.85% | -12.3% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4206 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4206 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4206 | 6.73% | 30.93% | 1.47% | 3.78% |
| UPRO | 4206 | 3.23% | 21.35% | 0.71% | 1.83% |
| SQQQ | 4206 | 9.99% | 28.96% | 1.52% | 5.02% |
| SPXU | 4206 | 5.71% | 18.81% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 5 trades, $-1.32; SPXU 5 trades, $-32.03; SPY 5 trades, $-9.24; SQQQ 2 trades, $+36.46; TQQQ 2 trades, $-11.99; UPRO 4 trades, $-47.88 · exits {'eod': 22, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 6 trades, $-16.57; SPXU 10 trades, $+12.31; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 3 trades, $-28.77 · exits {'eod': 23}
- **Volume spike:** QQQ 8 trades, $+17.43; SPXU 10 trades, $+57.41; SPY 4 trades, $-6.10; SQQQ 2 trades, $-0.16; UPRO 9 trades, $-28.94 · exits {'eod': 31, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-19.78; SPXU 7 trades, $+31.46; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-26.74 · exits {'eod': 23}
- **CVD turn 3-min (SPY):** SPY 33 trades, $-23.80 · exits {'cvd_sell': 32, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 33 trades, $+6.81 · exits {'cvd_sell': 30, 'stop': 3}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
