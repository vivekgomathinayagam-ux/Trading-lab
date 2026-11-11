# Trading Floor day-trade lab

Run 2026-11-11T01:18+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-10, 29 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 20 | 30.0% | 1.29% | -0.75% | -0.141% | 0.73 | -2.99% | -3.85% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 21 | 28.6% | 0.68% | -0.44% | -0.122% | 0.61 | -2.6% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 29 | 48.3% | 0.94% | -0.68% | 0.102% | 1.29 | 2.79% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 20 | 35.0% | 0.64% | -0.35% | -0.005% | 0.98 | -0.15% | -2.37% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 29 | 41.4% | 0.14% | -0.2% | -0.058% | 0.5 | -1.7% | -2.07% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 29 | 55.2% | 0.78% | -0.53% | 0.191% | 1.8 | 5.56% | -4.8% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 29 | 31.0% | 1.64% | -0.68% | 0.042% | 1.09 | 0.84% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 24 | 29.2% | 1.29% | -0.67% | -0.096% | 0.8 | -2.53% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 29 | 48.3% | 1.34% | -0.91% | 0.178% | 1.38 | 4.95% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -1.89%, QQQ -9.13%, TQQQ -28.32%, UPRO -7.82%, SQQQ +27.94%, SPXU +5.35%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 20 | -0.284% | -5.73% |
| EMA 9/21 + volume | 21 | -0.288% | -5.95% |
| Volume spike | 29 | -0.063% | -2.03% |
| EMA 9/21 + volume v2 | 20 | -0.167% | -3.34% |
| CVD turn 3-min (SPY) | 29 | -0.12% | -3.45% |
| CVD turn 3-min (TQQQ) | 29 | 0.01% | 0.16% |
| ORB (no volume filter) | 29 | -0.07% | -2.37% |
| EMA 9/21 (no volume filter) | 24 | -0.22% | -5.37% |
| Volume spike (2x) | 29 | 0.018% | 0.18% |

## Robustness check: 5-minute bars, 2026-09-17 to 2026-11-10 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 30.0% | -0.321% | 0.54 | -6.46% | -11.58% |
| EMA 9/21 + volume | 14 | 42.9% | -0.113% | 0.41 | -1.58% | -2.07% |
| Volume spike | 36 | 30.6% | -0.28% | 0.51 | -9.86% | -16.32% |
| EMA 9/21 + volume v2 | 14 | 42.9% | -0.113% | 0.41 | -1.58% | -2.07% |
| CVD turn 3-min (SPY) | 39 | 53.8% | -0.018% | 0.7 | -0.71% | -1.21% |
| CVD turn 3-min (TQQQ) | 39 | 51.3% | -0.114% | 0.69 | -4.5% | -5.5% |
| ORB (no volume filter) | 39 | 38.5% | -0.019% | 0.96 | -1.15% | -7.02% |
| EMA 9/21 (no volume filter) | 33 | 36.4% | -0.085% | 0.81 | -3.05% | -5.64% |
| Volume spike (2x) | 39 | 35.9% | -0.253% | 0.54 | -9.66% | -16.72% |

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

- **ORB + volume:** QQQ 3 trades, $-1.04; SPXU 5 trades, $-32.71; SPY 4 trades, $-1.85; SQQQ 2 trades, $+68.75; TQQQ 1 trades, $-9.44; UPRO 5 trades, $-53.62 · exits {'eod': 18, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 4 trades, $-16.36; SPXU 11 trades, $+4.78; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 3 trades, $-17.31 · exits {'eod': 21}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+52.73; SPY 2 trades, $+0.62; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 11 trades, $-27.84 · exits {'eod': 27, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 4 trades, $-16.36; SPXU 8 trades, $+23.88; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 2 trades, $-12.66 · exits {'eod': 20}
- **CVD turn 3-min (SPY):** SPY 29 trades, $-16.99 · exits {'cvd_sell': 28, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 29 trades, $+55.63 · exits {'cvd_sell': 27, 'stop': 2}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
