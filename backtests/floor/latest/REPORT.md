# Trading Floor day-trade lab

Run 2026-10-31T00:53+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-30, 22 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 15 | 33.3% | 0.56% | -0.66% | -0.254% | 0.43 | -3.81% | -3.54% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 15 | 26.7% | 0.3% | -0.44% | -0.245% | 0.25 | -3.63% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 22 | 54.5% | 0.9% | -0.64% | 0.198% | 1.68 | 4.3% | -3.24% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 14 | 35.7% | 0.34% | -0.32% | -0.085% | 0.59 | -1.19% | -2.37% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 22 | 36.4% | 0.13% | -0.09% | -0.008% | 0.86 | -0.18% | -0.48% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 22 | 63.6% | 0.84% | -0.12% | 0.492% | 12.41 | 11.35% | -0.83% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 22 | 31.8% | 1.31% | -0.8% | -0.127% | 0.77 | -3.0% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 18 | 33.3% | 0.7% | -0.61% | -0.172% | 0.57 | -3.15% | -5.78% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 22 | 50.0% | 1.03% | -0.9% | 0.064% | 1.14 | 1.25% | -3.24% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -1.13%, QQQ -7.01%, TQQQ -21.37%, UPRO -4.56%, SQQQ +22.85%, SPXU +4.17%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 15 | -0.386% | -5.71% |
| EMA 9/21 + volume | 15 | -0.426% | -6.22% |
| Volume spike | 22 | 0.003% | -0.09% |
| EMA 9/21 + volume v2 | 14 | -0.263% | -3.63% |
| CVD turn 3-min (SPY) | 22 | -0.07% | -1.53% |
| CVD turn 3-min (TQQQ) | 22 | 0.302% | 6.81% |
| ORB (no volume filter) | 22 | -0.245% | -5.49% |
| EMA 9/21 (no volume filter) | 18 | -0.308% | -5.49% |
| Volume spike (2x) | 22 | -0.111% | -2.57% |

## Robustness check: 5-minute bars, 2026-09-08 to 2026-10-30 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 21 | 38.1% | -0.492% | 0.21 | -9.93% | -11.47% |
| EMA 9/21 + volume | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| Volume spike | 36 | 25.0% | -0.53% | 0.15 | -17.52% | -17.26% |
| EMA 9/21 + volume v2 | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| CVD turn 3-min (SPY) | 39 | 56.4% | 0.005% | 1.14 | 0.2% | -0.76% |
| CVD turn 3-min (TQQQ) | 39 | 51.3% | -0.028% | 0.9 | -1.16% | -4.99% |
| ORB (no volume filter) | 39 | 41.0% | -0.11% | 0.75 | -4.47% | -7.05% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.062% | 0.81 | -2.24% | -5.69% |
| Volume spike (2x) | 39 | 35.9% | -0.326% | 0.37 | -12.09% | -12.96% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4194 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4194 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4194 | 6.68% | 30.9% | 1.48% | 3.77% |
| UPRO | 4194 | 3.22% | 21.29% | 0.72% | 1.84% |
| SQQQ | 4194 | 9.92% | 28.9% | 1.53% | 4.98% |
| SPXU | 4194 | 5.7% | 18.76% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 4 trades, $-1.85; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 3 trades, $-31.12 · exits {'eod': 14, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 10 trades, $-21.79; SPY 1 trades, $+2.66; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.72 · exits {'eod': 15}
- **Volume spike:** QQQ 3 trades, $+6.61; SPXU 9 trades, $+29.94; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 7 trades, $+6.64 · exits {'eod': 21, 'stop': 1}
- **EMA 9/21 + volume v2:** QQQ 1 trades, $-1.71; SPXU 7 trades, $-2.69; SPY 1 trades, $+2.66; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.85; UPRO 1 trades, $-10.07 · exits {'eod': 14}
- **CVD turn 3-min (SPY):** SPY 22 trades, $-1.75 · exits {'cvd_sell': 22}
- **CVD turn 3-min (TQQQ):** TQQQ 22 trades, $+113.50 · exits {'cvd_sell': 22}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
