# Trading Floor day-trade lab

Run 2026-10-28T22:40+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-28, 20 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 14 | 35.7% | 0.56% | -0.72% | -0.262% | 0.44 | -3.66% | -3.4% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 15 | 33.3% | 0.28% | -0.44% | -0.2% | 0.32 | -2.98% | -3.73% | 0 | loses or too thin after costs |
| Volume spike | yes | 20 | 55.0% | 0.9% | -0.7% | 0.179% | 1.57 | 3.5% | -3.24% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 20 | 35.0% | 1.31% | -0.86% | -0.1% | 0.82 | -2.22% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 17 | 35.3% | 0.7% | -0.65% | -0.175% | 0.58 | -3.03% | -5.67% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 20 | 50.0% | 1.04% | -0.97% | 0.032% | 1.07 | 0.47% | -3.24% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY +1.05%, QQQ -2.30%, TQQQ -8.33%, UPRO +2.13%, SQQQ +6.61%, SPXU -2.40%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 14 | -0.389% | -5.38% |
| EMA 9/21 + volume | 15 | -0.373% | -5.47% |
| Volume spike | 20 | -0.015% | -0.46% |
| ORB (no volume filter) | 20 | -0.222% | -4.59% |
| EMA 9/21 (no volume filter) | 17 | -0.315% | -5.31% |
| Volume spike (2x) | 20 | -0.141% | -2.94% |

## Robustness check: 5-minute bars, 2026-09-03 to 2026-10-28 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 40.0% | -0.496% | 0.22 | -9.55% | -8.84% |
| EMA 9/21 + volume | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| Volume spike | 36 | 27.8% | -0.51% | 0.17 | -16.92% | -15.04% |
| ORB (no volume filter) | 39 | 41.0% | -0.159% | 0.68 | -6.3% | -7.03% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.076% | 0.78 | -2.72% | -5.61% |
| Volume spike (2x) | 39 | 38.5% | -0.353% | 0.36 | -13.04% | -11.96% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4193 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4193 | 0.19% | 3.63% | 0.07% | 0.1% |
| TQQQ | 4193 | 6.68% | 30.91% | 1.48% | 3.77% |
| UPRO | 4193 | 3.22% | 21.3% | 0.72% | 1.84% |
| SQQQ | 4193 | 9.92% | 28.91% | 1.53% | 4.98% |
| SPXU | 4193 | 5.7% | 18.77% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 4 trades, $-1.85; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 2 trades, $-29.63 · exits {'eod': 13, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 10 trades, $-21.79; SPY 2 trades, $+4.53; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 15}
- **Volume spike:** QQQ 3 trades, $+6.61; SPXU 8 trades, $+20.39; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 6 trades, $+8.13 · exits {'eod': 19, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
