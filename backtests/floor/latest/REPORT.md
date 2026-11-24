# Trading Floor day-trade lab

Run 2026-11-24T05:22+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-23, 38 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 24 | 33.3% | 1.17% | -0.72% | -0.09% | 0.81 | -2.37% | -4.28% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 26 | 30.8% | 0.55% | -0.52% | -0.194% | 0.46 | -5.0% | -5.57% | 0 | loses or too thin after costs |
| Volume spike | yes | 38 | 50.0% | 1.22% | -0.8% | 0.208% | 1.52 | 7.78% | -3.27% | 1 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 25 | 36.0% | 0.53% | -0.47% | -0.113% | 0.63 | -2.85% | -4.26% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 38 | 34.2% | 1.95% | -0.76% | 0.167% | 1.34 | 5.93% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 31 | 32.3% | 1.51% | -0.72% | 0.0% | 1.0 | -0.4% | -5.78% | 2 | loses or too thin after costs |
| Volume spike (2x) | compare | 38 | 52.6% | 1.7% | -0.94% | 0.449% | 2.01 | 17.84% | -4.73% | 3 | promising, keep collecting |

Buy-and-hold over the same window: SPY -5.49%, QQQ -12.35%, TQQQ -37.72%, UPRO -19.03%, SQQQ +34.77%, SPXU +15.01%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 24 | -0.237% | -5.75% |
| EMA 9/21 + volume | 26 | -0.356% | -8.94% |
| Volume spike | 38 | 0.046% | 1.34% |
| EMA 9/21 + volume v2 | 25 | -0.262% | -6.41% |
| ORB (no volume filter) | 38 | 0.05% | 1.3% |
| EMA 9/21 (no volume filter) | 31 | -0.121% | -4.06% |
| Volume spike (2x) | 38 | 0.291% | 11.01% |

## Robustness check: 5-minute bars, 2026-10-01 to 2026-11-23 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 15 | 33.3% | -0.116% | 0.81 | -1.93% | -6.48% |
| EMA 9/21 + volume | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| Volume spike | 32 | 40.6% | -0.015% | 0.97 | -0.85% | -13.69% |
| EMA 9/21 + volume v2 | 10 | 40.0% | -0.113% | 0.44 | -1.13% | -1.99% |
| ORB (no volume filter) | 38 | 31.6% | 0.149% | 1.26 | 5.07% | -5.78% |
| EMA 9/21 (no volume filter) | 31 | 35.5% | 0.008% | 1.02 | -0.16% | -5.66% |
| Volume spike (2x) | 37 | 35.1% | -0.261% | 0.63 | -9.65% | -14.57% |

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

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 6 trades, $-37.71; SPY 4 trades, $-1.85; SQQQ 3 trades, $+84.28; TQQQ 2 trades, $-13.92; UPRO 5 trades, $-53.62 · exits {'eod': 22, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-14.90; SPXU 12 trades, $+6.28; SPY 2 trades, $+0.25; SQQQ 1 trades, $+1.05; TQQQ 2 trades, $-11.07; UPRO 4 trades, $-31.60 · exits {'eod': 26}
- **Volume spike:** QQQ 5 trades, $-16.18; SPXU 11 trades, $+108.17; SPY 4 trades, $-1.10; SQQQ 4 trades, $-13.48; TQQQ 2 trades, $+36.93; UPRO 12 trades, $-36.45 · exits {'eod': 33, 'stop': 4, 'target': 1}
- **EMA 9/21 + volume v2:** QQQ 5 trades, $-14.90; SPXU 9 trades, $+25.28; SPY 2 trades, $+0.25; SQQQ 4 trades, $+1.85; TQQQ 2 trades, $-11.71; UPRO 3 trades, $-29.33 · exits {'eod': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
