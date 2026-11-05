# Trading Floor day-trade lab

Run 2026-11-05T01:31+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-04, 25 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 18 | 27.8% | 0.56% | -0.59% | -0.272% | 0.37 | -4.84% | -4.58% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 18 | 33.3% | 0.7% | -0.43% | -0.054% | 0.81 | -1.03% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 25 | 44.0% | 0.84% | -0.67% | -0.006% | 0.98 | -0.32% | -3.27% | 0 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 18 | 38.9% | 0.66% | -0.32% | 0.062% | 1.32 | 1.08% | -2.09% | 0 | promising, keep collecting |
| CVD turn 3-min (SPY) | yes | 25 | 52.0% | 0.1% | -0.1% | 0.005% | 1.11 | 0.13% | -0.63% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 25 | 64.0% | 0.75% | -0.33% | 0.362% | 4.09 | 9.38% | -2.15% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 25 | 28.0% | 1.31% | -0.72% | -0.152% | 0.71 | -3.98% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 21 | 33.3% | 1.29% | -0.7% | -0.038% | 0.92 | -1.04% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 25 | 44.0% | 0.91% | -0.95% | -0.128% | 0.76 | -3.34% | -5.22% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY +0.31%, QQQ -6.84%, TQQQ -21.13%, UPRO -0.49%, SQQQ +22.11%, SPXU -0.29%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 18 | -0.393% | -6.91% |
| EMA 9/21 + volume | 18 | -0.21% | -3.77% |
| Volume spike | 25 | -0.171% | -4.36% |
| EMA 9/21 + volume v2 | 18 | -0.08% | -1.49% |
| CVD turn 3-min (SPY) | 25 | -0.056% | -1.41% |
| CVD turn 3-min (TQQQ) | 25 | 0.167% | 4.18% |
| ORB (no volume filter) | 25 | -0.27% | -6.76% |
| EMA 9/21 (no volume filter) | 21 | -0.169% | -3.72% |
| Volume spike (2x) | 25 | -0.296% | -7.33% |

## Robustness check: 5-minute bars, 2026-09-11 to 2026-11-04 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 21 | 38.1% | -0.311% | 0.43 | -6.43% | -9.48% |
| EMA 9/21 + volume | 18 | 44.4% | -0.231% | 0.25 | -4.1% | -4.33% |
| Volume spike | 36 | 41.7% | -0.342% | 0.38 | -11.79% | -14.35% |
| EMA 9/21 + volume v2 | 18 | 44.4% | -0.231% | 0.25 | -4.1% | -4.33% |
| CVD turn 3-min (SPY) | 39 | 51.3% | -0.015% | 0.7 | -0.6% | -0.65% |
| CVD turn 3-min (TQQQ) | 39 | 48.7% | -0.106% | 0.68 | -4.15% | -5.17% |
| ORB (no volume filter) | 39 | 38.5% | -0.142% | 0.7 | -5.67% | -7.03% |
| EMA 9/21 (no volume filter) | 34 | 41.2% | 0.019% | 1.05 | 0.33% | -5.71% |
| Volume spike (2x) | 39 | 38.5% | -0.295% | 0.47 | -11.09% | -12.25% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4197 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4197 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4197 | 6.67% | 30.93% | 1.48% | 3.76% |
| UPRO | 4197 | 3.22% | 21.32% | 0.71% | 1.83% |
| SQQQ | 4197 | 9.96% | 28.88% | 1.52% | 5.0% |
| SPXU | 4197 | 5.69% | 18.75% | 0.69% | 2.76% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-1.54; SPXU 4 trades, $-18.49; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 3 trades, $-31.36 · exits {'eod': 17, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 4 trades, $-7.60; SPXU 9 trades, $+10.91; SPY 2 trades, $+1.64; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 18}
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 9 trades, $+29.85; SPY 1 trades, $-1.58; SQQQ 1 trades, $-16.43; UPRO 8 trades, $-27.07 · exits {'eod': 23, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 5 trades, $-10.81; SPXU 6 trades, $+30.06; SPY 2 trades, $+1.64; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 18}
- **CVD turn 3-min (SPY):** SPY 25 trades, $+1.32 · exits {'cvd_sell': 25}
- **CVD turn 3-min (TQQQ):** TQQQ 25 trades, $+93.79 · exits {'cvd_sell': 25}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
