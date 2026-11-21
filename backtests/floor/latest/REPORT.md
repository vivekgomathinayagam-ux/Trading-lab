# Trading Floor day-trade lab

Run 2026-11-21T02:32+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-20, 37 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 24 | 33.3% | 1.17% | -0.72% | -0.09% | 0.81 | -2.37% | -4.28% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 25 | 32.0% | 0.55% | -0.54% | -0.192% | 0.48 | -4.76% | -5.48% | 0 | loses or too thin after costs |
| Volume spike | yes | 37 | 51.4% | 1.22% | -0.71% | 0.281% | 1.81 | 10.52% | -3.27% | 1 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 24 | 37.5% | 0.53% | -0.49% | -0.107% | 0.65 | -2.61% | -4.17% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 37 | 35.1% | 1.95% | -0.78% | 0.182% | 1.36 | 6.32% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 30 | 33.3% | 1.51% | -0.63% | 0.084% | 1.2 | 2.19% | -5.78% | 2 | promising, keep collecting |
| Volume spike (2x) | compare | 37 | 54.1% | 1.7% | -0.96% | 0.476% | 2.08 | 18.46% | -4.73% | 3 | promising, keep collecting |

Buy-and-hold over the same window: SPY -9.61%, QQQ -17.85%, TQQQ -48.02%, UPRO -28.69%, SQQQ +69.13%, SPXU +33.56%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 24 | -0.237% | -5.75% |
| EMA 9/21 + volume | 25 | -0.357% | -8.64% |
| Volume spike | 37 | 0.118% | 4.07% |
| EMA 9/21 + volume v2 | 24 | -0.26% | -6.11% |
| ORB (no volume filter) | 37 | 0.063% | 1.75% |
| EMA 9/21 (no volume filter) | 30 | -0.038% | -1.49% |
| Volume spike (2x) | 37 | 0.319% | 11.84% |

## Robustness check: 5-minute bars, 2026-09-28 to 2026-11-20 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 17 | 29.4% | -0.25% | 0.64 | -4.4% | -8.58% |
| EMA 9/21 + volume | 11 | 36.4% | -0.129% | 0.38 | -1.42% | -2.0% |
| Volume spike | 35 | 40.0% | -0.048% | 0.91 | -2.05% | -16.1% |
| EMA 9/21 + volume v2 | 11 | 36.4% | -0.129% | 0.38 | -1.42% | -2.0% |
| ORB (no volume filter) | 40 | 35.0% | 0.161% | 1.3 | 5.91% | -7.07% |
| EMA 9/21 (no volume filter) | 33 | 39.4% | 0.113% | 1.3 | 3.44% | -5.72% |
| Volume spike (2x) | 40 | 35.0% | -0.267% | 0.62 | -10.56% | -16.96% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4210 | 0.17% | 1.73% | 0.05% | 0.02% |
| QQQ | 4210 | 0.19% | 3.68% | 0.07% | 0.1% |
| TQQQ | 4210 | 6.72% | 31.0% | 1.47% | 3.78% |
| UPRO | 4210 | 3.23% | 21.43% | 0.71% | 1.83% |
| SQQQ | 4210 | 10.05% | 28.93% | 1.52% | 5.06% |
| SPXU | 4210 | 5.75% | 18.79% | 0.69% | 2.83% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 6 trades, $-37.71; SPY 4 trades, $-1.85; SQQQ 3 trades, $+84.28; TQQQ 2 trades, $-13.92; UPRO 5 trades, $-53.62 · exits {'eod': 22, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-14.90; SPXU 12 trades, $+6.28; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 2 trades, $-11.07; UPRO 4 trades, $-31.60 · exits {'eod': 25}
- **Volume spike:** QQQ 5 trades, $-16.18; SPXU 11 trades, $+108.17; SPY 4 trades, $-1.10; SQQQ 3 trades, $+13.90; TQQQ 2 trades, $+36.93; UPRO 12 trades, $-36.45 · exits {'eod': 33, 'stop': 3, 'target': 1}
- **EMA 9/21 + volume v2:** QQQ 5 trades, $-14.90; SPXU 9 trades, $+25.28; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 2 trades, $-11.71; UPRO 3 trades, $-29.33 · exits {'eod': 24}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
