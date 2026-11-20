# Trading Floor day-trade lab

Run 2026-11-20T02:14+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-19, 36 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 24 | 29.2% | 0.64% | -0.69% | -0.302% | 0.38 | -7.09% | -7.82% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 25 | 36.0% | 0.51% | -0.53% | -0.154% | 0.54 | -3.86% | -4.59% | 0 | loses or too thin after costs |
| Volume spike | yes | 36 | 47.2% | 0.93% | -0.65% | 0.094% | 1.27 | 3.21% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 25 | 40.0% | 0.51% | -0.46% | -0.073% | 0.74 | -1.89% | -4.02% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 36 | 36.1% | 1.95% | -0.74% | 0.233% | 1.49 | 8.12% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 30 | 33.3% | 1.51% | -0.63% | 0.084% | 1.2 | 2.19% | -5.78% | 2 | promising, keep collecting |
| Volume spike (2x) | compare | 36 | 50.0% | 1.44% | -0.89% | 0.275% | 1.62 | 9.86% | -5.22% | 2 | promising, keep collecting |

Buy-and-hold over the same window: SPY -6.36%, QQQ -13.13%, TQQQ -37.87%, UPRO -20.32%, SQQQ +45.16%, SPXU +20.77%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 24 | -0.437% | -10.07% |
| EMA 9/21 + volume | 25 | -0.314% | -7.64% |
| Volume spike | 36 | -0.06% | -2.35% |
| EMA 9/21 + volume v2 | 25 | -0.217% | -5.35% |
| ORB (no volume filter) | 36 | 0.114% | 3.58% |
| EMA 9/21 (no volume filter) | 30 | -0.038% | -1.49% |
| Volume spike (2x) | 36 | 0.122% | 3.99% |

## Robustness check: 5-minute bars, 2026-09-25 to 2026-11-19 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 36.8% | -0.185% | 0.7 | -3.69% | -9.61% |
| EMA 9/21 + volume | 13 | 30.8% | -0.311% | 0.17 | -4.0% | -4.33% |
| Volume spike | 36 | 47.2% | -0.09% | 0.82 | -3.51% | -13.52% |
| EMA 9/21 + volume v2 | 13 | 30.8% | -0.311% | 0.17 | -4.0% | -4.33% |
| ORB (no volume filter) | 40 | 37.5% | 0.209% | 1.43 | 7.99% | -7.05% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | 0.062% | 1.14 | 1.73% | -5.64% |
| Volume spike (2x) | 40 | 42.5% | 0.001% | 1.0 | -0.42% | -11.98% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4208 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4208 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4208 | 6.73% | 30.96% | 1.47% | 3.78% |
| UPRO | 4208 | 3.23% | 21.39% | 0.71% | 1.83% |
| SQQQ | 4208 | 10.0% | 28.94% | 1.52% | 5.01% |
| SPXU | 4208 | 5.7% | 18.8% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 5 trades, $-1.32; SPXU 6 trades, $-36.96; SPY 5 trades, $-9.24; SQQQ 2 trades, $+36.46; TQQQ 2 trades, $-11.99; UPRO 4 trades, $-47.88 · exits {'eod': 23, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 6 trades, $-12.45; SPXU 11 trades, $+11.90; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 4 trades, $-39.98 · exits {'eod': 25}
- **Volume spike:** QQQ 8 trades, $-1.80; SPXU 10 trades, $+57.41; SPY 4 trades, $-6.10; SQQQ 3 trades, $+13.16; UPRO 11 trades, $-30.54 · exits {'eod': 33, 'stop': 3}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-15.66; SPXU 8 trades, $+32.03; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 3 trades, $-37.95 · exits {'eod': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
