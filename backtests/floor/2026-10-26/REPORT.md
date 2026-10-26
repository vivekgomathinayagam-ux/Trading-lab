# Trading Floor day-trade lab

Run 2026-10-26T04:40+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-23, 17 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 12 | 33.3% | 0.81% | -0.73% | -0.218% | 0.55 | -2.65% | -2.87% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 11 | 36.4% | 0.3% | -0.53% | -0.228% | 0.33 | -2.51% | -3.21% | 0 | loses or too thin after costs |
| Volume spike | yes | 17 | 47.1% | 0.94% | -0.7% | 0.074% | 1.2 | 1.13% | -3.27% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 17 | 35.3% | 1.52% | -0.77% | 0.035% | 1.07 | 0.37% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 14 | 42.9% | 0.7% | -0.46% | 0.037% | 1.14 | 0.46% | -2.3% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 17 | 47.1% | 1.04% | -0.87% | 0.025% | 1.05 | 0.28% | -3.26% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -0.58%, QQQ -5.14%, TQQQ -15.96%, UPRO -2.64%, SQQQ +16.56%, SPXU +2.43%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 12 | -0.357% | -4.26% |
| EMA 9/21 + volume | 11 | -0.391% | -4.24% |
| Volume spike | 17 | -0.133% | -2.38% |
| ORB (no volume filter) | 17 | -0.082% | -1.61% |
| EMA 9/21 (no volume filter) | 14 | -0.085% | -1.24% |
| Volume spike (2x) | 17 | -0.143% | -2.53% |

## Robustness check: 5-minute bars, 2026-09-02 to 2026-10-23 (37 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 42.1% | -0.402% | 0.3 | -7.46% | -7.46% |
| EMA 9/21 + volume | 14 | 50.0% | -0.079% | 0.51 | -1.11% | -1.31% |
| Volume spike | 34 | 35.3% | -0.407% | 0.24 | -13.06% | -13.0% |
| ORB (no volume filter) | 37 | 40.5% | -0.123% | 0.74 | -4.75% | -8.92% |
| EMA 9/21 (no volume filter) | 32 | 43.8% | 0.034% | 1.13 | 0.96% | -2.28% |
| Volume spike (2x) | 37 | 40.5% | -0.253% | 0.52 | -9.17% | -7.59% |

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

- **ORB + volume:** QQQ 2 trades, $-1.73; SPXU 4 trades, $-18.49; SPY 2 trades, $-1.49; SQQQ 1 trades, $+21.67; TQQQ 2 trades, $-2.33; UPRO 1 trades, $-24.13 · exits {'eod': 11, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-2.66; SPXU 7 trades, $-14.55; SPY 2 trades, $+2.20; UPRO 1 trades, $-10.07 · exits {'eod': 11}
- **Volume spike:** QQQ 3 trades, $+6.01; SPXU 8 trades, $+20.63; SQQQ 1 trades, $-16.43; UPRO 5 trades, $+1.12 · exits {'eod': 16, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
