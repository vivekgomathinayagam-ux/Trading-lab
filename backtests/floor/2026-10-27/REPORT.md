# Trading Floor day-trade lab

Run 2026-10-27T00:46+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-26, 18 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 13 | 38.5% | 0.56% | -0.8% | -0.274% | 0.44 | -3.57% | -3.36% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 13 | 38.5% | 0.28% | -0.47% | -0.181% | 0.37 | -2.35% | -3.1% | 0 | loses or too thin after costs |
| Volume spike | yes | 18 | 50.0% | 0.87% | -0.7% | 0.086% | 1.25 | 1.43% | -3.24% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 18 | 38.9% | 1.31% | -0.77% | 0.036% | 1.08 | 0.42% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 15 | 40.0% | 0.7% | -0.42% | 0.026% | 1.1 | 0.32% | -2.41% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 18 | 50.0% | 0.95% | -0.88% | 0.038% | 1.09 | 0.55% | -3.24% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY +0.11%, QQQ -4.10%, TQQQ -13.25%, UPRO -0.61%, SQQQ +12.85%, SPXU +0.29%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 13 | -0.406% | -5.22% |
| EMA 9/21 + volume | 13 | -0.349% | -4.46% |
| Volume spike | 18 | -0.12% | -2.26% |
| ORB (no volume filter) | 18 | -0.078% | -1.63% |
| EMA 9/21 (no volume filter) | 15 | -0.101% | -1.58% |
| Volume spike (2x) | 18 | -0.129% | -2.43% |

## Robustness check: 5-minute bars, 2026-09-03 to 2026-10-26 (37 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 45.0% | -0.486% | 0.23 | -9.37% | -8.74% |
| EMA 9/21 + volume | 13 | 46.2% | -0.112% | 0.39 | -1.46% | -1.62% |
| Volume spike | 34 | 29.4% | -0.483% | 0.18 | -15.3% | -13.43% |
| ORB (no volume filter) | 37 | 43.2% | -0.078% | 0.82 | -3.12% | -7.03% |
| EMA 9/21 (no volume filter) | 32 | 40.6% | 0.026% | 1.1 | 0.7% | -2.32% |
| Volume spike (2x) | 37 | 40.5% | -0.32% | 0.39 | -11.36% | -10.3% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4190 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4190 | 0.19% | 3.63% | 0.07% | 0.1% |
| TQQQ | 4190 | 6.68% | 30.93% | 1.48% | 3.77% |
| UPRO | 4190 | 3.22% | 21.31% | 0.72% | 1.84% |
| SQQQ | 4190 | 9.93% | 28.88% | 1.53% | 4.99% |
| SPXU | 4190 | 5.7% | 18.78% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 3 trades, $-0.87; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 2 trades, $-29.63 · exits {'eod': 12, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 9 trades, $-16.22; SPY 2 trades, $+4.53; UPRO 1 trades, $-10.07 · exits {'eod': 13}
- **Volume spike:** QQQ 2 trades, $+4.32; SPXU 8 trades, $+20.39; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; UPRO 6 trades, $+8.13 · exits {'eod': 17, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
