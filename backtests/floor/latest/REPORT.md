# Trading Floor day-trade lab

Run 2026-11-25T02:14+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-24, 39 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 25 | 32.0% | 1.17% | -0.82% | -0.185% | 0.67 | -4.77% | -5.62% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 27 | 29.6% | 0.55% | -0.52% | -0.203% | 0.44 | -5.41% | -5.98% | 0 | loses or too thin after costs |
| Volume spike | yes | 39 | 48.7% | 1.22% | -0.89% | 0.138% | 1.3 | 5.05% | -4.95% | 1 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 26 | 34.6% | 0.53% | -0.47% | -0.125% | 0.59 | -3.27% | -4.67% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 39 | 33.3% | 1.95% | -0.73% | 0.161% | 1.33 | 5.85% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 32 | 31.2% | 1.51% | -0.69% | -0.001% | 1.0 | -0.42% | -5.78% | 2 | loses or too thin after costs |
| Volume spike (2x) | compare | 39 | 51.3% | 1.7% | -1.02% | 0.374% | 1.75 | 14.89% | -4.73% | 3 | promising, keep collecting |

Buy-and-hold over the same window: SPY -5.96%, QQQ -14.07%, TQQQ -41.46%, UPRO -20.28%, SQQQ +42.76%, SPXU +16.81%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 25 | -0.32% | -7.93% |
| EMA 9/21 + volume | 27 | -0.364% | -9.46% |
| Volume spike | 39 | -0.022% | -1.28% |
| EMA 9/21 + volume v2 | 26 | -0.273% | -6.94% |
| ORB (no volume filter) | 39 | 0.045% | 1.17% |
| EMA 9/21 (no volume filter) | 32 | -0.119% | -4.13% |
| Volume spike (2x) | 39 | 0.218% | 8.16% |

## Robustness check: 5-minute bars, 2026-10-01 to 2026-11-24 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 15 | 33.3% | -0.116% | 0.81 | -1.93% | -6.48% |
| EMA 9/21 + volume | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| Volume spike | 33 | 39.4% | -0.015% | 0.97 | -0.89% | -13.69% |
| EMA 9/21 + volume v2 | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| ORB (no volume filter) | 39 | 30.8% | 0.145% | 1.26 | 5.07% | -5.78% |
| EMA 9/21 (no volume filter) | 32 | 34.4% | 0.007% | 1.02 | -0.17% | -5.66% |
| Volume spike (2x) | 38 | 34.2% | -0.255% | 0.63 | -9.68% | -14.57% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4211 | 0.17% | 1.73% | 0.05% | 0.02% |
| QQQ | 4211 | 0.19% | 3.68% | 0.07% | 0.09% |
| TQQQ | 4211 | 6.72% | 31.01% | 1.47% | 3.78% |
| UPRO | 4211 | 3.23% | 21.44% | 0.71% | 1.83% |
| SQQQ | 4211 | 10.07% | 28.92% | 1.52% | 5.06% |
| SPXU | 4211 | 5.77% | 18.78% | 0.69% | 2.83% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 6 trades, $-37.71; SPY 4 trades, $-1.85; SQQQ 3 trades, $+84.28; TQQQ 2 trades, $-13.92; UPRO 6 trades, $-77.62 · exits {'eod': 22, 'stop': 2, 'target': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-14.90; SPXU 12 trades, $+6.28; SPY 2 trades, $+0.25; SQQQ 1 trades, $+1.05; TQQQ 2 trades, $-11.07; UPRO 5 trades, $-35.74 · exits {'eod': 27}
- **Volume spike:** QQQ 5 trades, $-16.18; SPXU 12 trades, $+80.80; SPY 4 trades, $-1.10; SQQQ 4 trades, $-13.48; TQQQ 2 trades, $+36.93; UPRO 12 trades, $-36.45 · exits {'eod': 33, 'stop': 5, 'target': 1}
- **EMA 9/21 + volume v2:** QQQ 5 trades, $-14.90; SPXU 9 trades, $+25.28; SPY 2 trades, $+0.25; SQQQ 4 trades, $+1.85; TQQQ 2 trades, $-11.71; UPRO 4 trades, $-33.47 · exits {'eod': 26}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
