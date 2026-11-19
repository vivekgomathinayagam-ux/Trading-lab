# Trading Floor day-trade lab

Run 2026-11-19T02:40+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-18, 35 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 24 | 33.3% | 1.17% | -0.72% | -0.09% | 0.81 | -2.37% | -4.28% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 25 | 32.0% | 0.55% | -0.54% | -0.192% | 0.48 | -4.76% | -5.48% | 0 | loses or too thin after costs |
| Volume spike | yes | 35 | 51.4% | 1.02% | -0.66% | 0.205% | 1.64 | 7.15% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 24 | 37.5% | 0.53% | -0.49% | -0.107% | 0.65 | -2.61% | -4.17% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 35 | 34.3% | 1.71% | -0.74% | 0.1% | 1.21 | 3.08% | -6.64% | 2 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 29 | 31.0% | 1.14% | -0.63% | -0.079% | 0.82 | -2.52% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 35 | 51.4% | 1.34% | -0.96% | 0.224% | 1.48 | 7.68% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -4.45%, QQQ -11.19%, TQQQ -33.49%, UPRO -15.23%, SQQQ +36.12%, SPXU +13.91%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 24 | -0.237% | -5.75% |
| EMA 9/21 + volume | 25 | -0.357% | -8.64% |
| Volume spike | 35 | 0.036% | 1.03% |
| EMA 9/21 + volume v2 | 24 | -0.26% | -6.11% |
| ORB (no volume filter) | 35 | -0.019% | -1.14% |
| EMA 9/21 (no volume filter) | 29 | -0.201% | -5.91% |
| Volume spike (2x) | 35 | 0.066% | 1.92% |

## Robustness check: 5-minute bars, 2026-09-24 to 2026-11-18 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 31.6% | -0.338% | 0.54 | -6.46% | -9.96% |
| EMA 9/21 + volume | 12 | 41.7% | -0.111% | 0.41 | -1.34% | -2.0% |
| Volume spike | 36 | 38.9% | -0.155% | 0.72 | -5.73% | -16.2% |
| EMA 9/21 + volume v2 | 12 | 41.7% | -0.111% | 0.41 | -1.34% | -2.0% |
| ORB (no volume filter) | 40 | 37.5% | 0.089% | 1.18 | 3.02% | -7.04% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.081% | 0.81 | -2.99% | -5.64% |
| Volume spike (2x) | 40 | 35.0% | -0.327% | 0.5 | -12.57% | -16.84% |

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

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 6 trades, $-37.71; SPY 4 trades, $-1.85; SQQQ 3 trades, $+84.28; TQQQ 2 trades, $-13.92; UPRO 5 trades, $-53.62 · exits {'eod': 22, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-14.90; SPXU 12 trades, $+6.28; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 2 trades, $-11.07; UPRO 4 trades, $-31.60 · exits {'eod': 25}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+57.74; SPY 4 trades, $-1.10; SQQQ 3 trades, $+13.90; TQQQ 2 trades, $+36.93; UPRO 12 trades, $-36.45 · exits {'eod': 33, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 5 trades, $-14.90; SPXU 9 trades, $+25.28; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 2 trades, $-11.71; UPRO 3 trades, $-29.33 · exits {'eod': 24}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
