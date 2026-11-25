# Trading Floor day-trade lab

Run 2026-11-25T04:21+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-24, 39 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 25 | 28.0% | 0.64% | -0.8% | -0.4% | 0.31 | -9.65% | -9.4% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 27 | 33.3% | 0.51% | -0.51% | -0.168% | 0.5 | -4.52% | -5.09% | 0 | loses or too thin after costs |
| Volume spike | yes | 39 | 46.2% | 1.15% | -0.83% | 0.083% | 1.18 | 2.85% | -4.96% | 1 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 27 | 37.0% | 0.51% | -0.45% | -0.093% | 0.67 | -2.55% | -4.52% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 39 | 33.3% | 1.95% | -0.73% | 0.161% | 1.33 | 5.85% | -6.64% | 3 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 32 | 31.2% | 1.51% | -0.69% | -0.001% | 1.0 | -0.42% | -5.78% | 2 | loses or too thin after costs |
| Volume spike (2x) | compare | 39 | 48.7% | 1.61% | -0.95% | 0.298% | 1.61 | 11.62% | -5.24% | 3 | promising, keep collecting |

Buy-and-hold over the same window: SPY -5.96%, QQQ -14.07%, TQQQ -41.46%, UPRO -20.26%, SQQQ +42.76%, SPXU +16.81%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 25 | -0.543% | -12.83% |
| EMA 9/21 + volume | 27 | -0.324% | -8.46% |
| Volume spike | 39 | -0.07% | -3.08% |
| EMA 9/21 + volume v2 | 27 | -0.233% | -6.17% |
| ORB (no volume filter) | 39 | 0.045% | 1.16% |
| EMA 9/21 (no volume filter) | 32 | -0.119% | -4.13% |
| Volume spike (2x) | 39 | 0.147% | 5.22% |

## Robustness check: 5-minute bars, 2026-10-01 to 2026-11-24 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 16 | 37.5% | -0.091% | 0.84 | -1.65% | -6.3% |
| EMA 9/21 + volume | 12 | 33.3% | -0.312% | 0.19 | -3.71% | -4.31% |
| Volume spike | 33 | 48.5% | 0.068% | 1.15 | 1.89% | -11.29% |
| EMA 9/21 + volume v2 | 12 | 33.3% | -0.312% | 0.19 | -3.71% | -4.31% |
| ORB (no volume filter) | 39 | 30.8% | 0.148% | 1.27 | 5.2% | -5.76% |
| EMA 9/21 (no volume filter) | 32 | 34.4% | 0.006% | 1.01 | -0.21% | -5.72% |
| Volume spike (2x) | 38 | 39.5% | -0.064% | 0.89 | -2.88% | -10.87% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4212 | 0.17% | 1.73% | 0.05% | 0.02% |
| QQQ | 4212 | 0.19% | 3.68% | 0.07% | 0.09% |
| TQQQ | 4212 | 6.72% | 31.03% | 1.47% | 3.77% |
| UPRO | 4212 | 3.23% | 21.44% | 0.71% | 1.83% |
| SQQQ | 4212 | 10.07% | 28.92% | 1.52% | 5.06% |
| SPXU | 4212 | 5.77% | 18.78% | 0.69% | 2.83% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.39; SPXU 6 trades, $-36.96; SPY 5 trades, $-9.21; SQQQ 2 trades, $+36.46; TQQQ 2 trades, $-11.99; UPRO 6 trades, $-74.38 · exits {'eod': 23, 'stop': 2}
- **EMA 9/21 + volume:** QQQ 6 trades, $-12.45; SPXU 11 trades, $+11.90; SPY 3 trades, $-0.77; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 5 trades, $-44.12 · exits {'eod': 27}
- **Volume spike:** QQQ 7 trades, $-0.10; SPXU 12 trades, $+81.52; SPY 5 trades, $-8.16; SQQQ 4 trades, $-14.22; UPRO 11 trades, $-30.54 · exits {'eod': 33, 'stop': 5, 'target': 1}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-15.66; SPXU 8 trades, $+32.03; SPY 3 trades, $-0.77; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 4 trades, $-42.09 · exits {'eod': 27}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
