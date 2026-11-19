# Trading Floor day-trade lab

Run 2026-11-19T02:14+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-18, 35 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 24 | 29.2% | 0.64% | -0.69% | -0.302% | 0.38 | -7.09% | -7.82% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 25 | 36.0% | 0.51% | -0.53% | -0.154% | 0.54 | -3.86% | -4.59% | 0 | loses or too thin after costs |
| Volume spike | yes | 35 | 48.6% | 0.91% | -0.6% | 0.13% | 1.42 | 4.44% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 25 | 40.0% | 0.51% | -0.46% | -0.073% | 0.74 | -1.89% | -4.02% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 35 | 34.3% | 1.71% | -0.74% | 0.1% | 1.21 | 3.08% | -6.64% | 2 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 29 | 31.0% | 1.14% | -0.63% | -0.079% | 0.82 | -2.53% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 35 | 48.6% | 1.24% | -0.89% | 0.144% | 1.31 | 4.76% | -5.22% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -4.45%, QQQ -11.19%, TQQQ -33.49%, UPRO -15.23%, SQQQ +36.12%, SPXU +13.91%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 24 | -0.437% | -10.07% |
| EMA 9/21 + volume | 25 | -0.314% | -7.64% |
| Volume spike | 35 | -0.022% | -0.97% |
| EMA 9/21 + volume v2 | 25 | -0.217% | -5.35% |
| ORB (no volume filter) | 35 | -0.02% | -1.15% |
| EMA 9/21 (no volume filter) | 29 | -0.201% | -5.91% |
| Volume spike (2x) | 35 | -0.012% | -0.79% |

## Robustness check: 5-minute bars, 2026-09-24 to 2026-11-18 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 35.0% | -0.181% | 0.69 | -3.78% | -9.62% |
| EMA 9/21 + volume | 14 | 35.7% | -0.282% | 0.19 | -3.91% | -4.32% |
| Volume spike | 37 | 48.6% | -0.063% | 0.87 | -2.64% | -13.87% |
| EMA 9/21 + volume v2 | 14 | 35.7% | -0.282% | 0.19 | -3.91% | -4.32% |
| ORB (no volume filter) | 40 | 37.5% | 0.092% | 1.19 | 3.15% | -7.04% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.078% | 0.82 | -2.9% | -5.63% |
| Volume spike (2x) | 40 | 40.0% | -0.144% | 0.74 | -5.95% | -12.3% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4207 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4207 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4207 | 6.73% | 30.95% | 1.47% | 3.78% |
| UPRO | 4207 | 3.23% | 21.37% | 0.71% | 1.83% |
| SQQQ | 4207 | 10.01% | 28.95% | 1.52% | 5.02% |
| SPXU | 4207 | 5.7% | 18.8% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 5 trades, $-1.32; SPXU 6 trades, $-36.96; SPY 5 trades, $-9.24; SQQQ 2 trades, $+36.46; TQQQ 2 trades, $-11.99; UPRO 4 trades, $-47.88 · exits {'eod': 23, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 6 trades, $-12.45; SPXU 11 trades, $+11.90; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 4 trades, $-39.98 · exits {'eod': 25}
- **Volume spike:** QQQ 8 trades, $+17.43; SPXU 10 trades, $+57.41; SPY 4 trades, $-6.10; SQQQ 3 trades, $+13.16; UPRO 10 trades, $-37.55 · exits {'eod': 33, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-15.66; SPXU 8 trades, $+32.03; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 3 trades, $-37.95 · exits {'eod': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
