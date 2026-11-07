# Trading Floor day-trade lab

Run 2026-11-07T00:59+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-06, 27 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 19 | 26.3% | 0.56% | -0.67% | -0.349% | 0.3 | -6.49% | -6.23% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 20 | 35.0% | 0.62% | -0.44% | -0.067% | 0.76 | -1.4% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 27 | 44.4% | 0.97% | -0.66% | 0.065% | 1.18 | 1.58% | -3.27% | 0 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 20 | 40.0% | 0.59% | -0.33% | 0.038% | 1.19 | 0.71% | -2.09% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 27 | 51.9% | 0.11% | -0.24% | -0.057% | 0.5 | -1.55% | -1.97% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 27 | 59.3% | 0.75% | -0.54% | 0.224% | 2.02 | 6.11% | -2.99% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 27 | 29.6% | 1.75% | -0.71% | 0.019% | 1.04 | 0.14% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 23 | 30.4% | 1.29% | -0.68% | -0.081% | 0.83 | -2.08% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 27 | 48.1% | 1.21% | -0.95% | 0.094% | 1.19 | 2.25% | -5.22% | 1 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -3.80%, QQQ -11.63%, TQQQ -33.76%, UPRO -12.87%, SQQQ +39.94%, SPXU +11.92%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 19 | -0.476% | -8.75% |
| EMA 9/21 + volume | 20 | -0.221% | -4.39% |
| Volume spike | 27 | -0.098% | -2.81% |
| EMA 9/21 + volume v2 | 20 | -0.104% | -2.1% |
| CVD turn 3-min (SPY) | 27 | -0.119% | -3.18% |
| CVD turn 3-min (TQQQ) | 27 | 0.034% | 0.79% |
| ORB (no volume filter) | 27 | -0.098% | -2.97% |
| EMA 9/21 (no volume filter) | 23 | -0.206% | -4.87% |
| Volume spike (2x) | 27 | -0.072% | -2.23% |

## Robustness check: 5-minute bars, 2026-09-14 to 2026-11-06 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 22 | 40.9% | -0.096% | 0.82 | -2.32% | -9.56% |
| EMA 9/21 + volume | 18 | 44.4% | -0.232% | 0.25 | -4.13% | -4.34% |
| Volume spike | 37 | 43.2% | -0.21% | 0.62 | -7.77% | -14.33% |
| EMA 9/21 + volume v2 | 18 | 44.4% | -0.232% | 0.25 | -4.13% | -4.34% |
| CVD turn 3-min (SPY) | 40 | 52.5% | -0.028% | 0.59 | -1.12% | -1.35% |
| CVD turn 3-min (TQQQ) | 40 | 47.5% | -0.166% | 0.57 | -6.57% | -6.05% |
| ORB (no volume filter) | 40 | 40.0% | -0.031% | 0.93 | -1.63% | -7.02% |
| EMA 9/21 (no volume filter) | 35 | 40.0% | -0.011% | 0.97 | -0.68% | -5.71% |
| Volume spike (2x) | 40 | 40.0% | -0.174% | 0.68 | -7.07% | -12.23% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4200 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4200 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4200 | 6.69% | 30.93% | 1.48% | 3.76% |
| UPRO | 4200 | 3.21% | 21.33% | 0.71% | 1.83% |
| SQQQ | 4200 | 9.98% | 28.9% | 1.52% | 5.02% |
| SPXU | 4200 | 5.71% | 18.79% | 0.69% | 2.79% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-1.54; SPXU 4 trades, $-18.49; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 4 trades, $-47.88 · exits {'eod': 18, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 5 trades, $-12.37; SPXU 9 trades, $+10.91; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 20}
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 10 trades, $+54.08; SPY 2 trades, $-6.85; SQQQ 1 trades, $-16.43; UPRO 8 trades, $-27.07 · exits {'eod': 25, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 6 trades, $-15.58; SPXU 6 trades, $+30.06; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 20}
- **CVD turn 3-min (SPY):** SPY 27 trades, $-15.50 · exits {'cvd_sell': 26, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 27 trades, $+61.12 · exits {'cvd_sell': 26, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
