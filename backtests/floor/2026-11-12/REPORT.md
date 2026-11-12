# Trading Floor day-trade lab

Run 2026-11-12T02:15+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-11, 30 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 21 | 33.3% | 1.11% | -0.75% | -0.134% | 0.73 | -2.97% | -3.85% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 22 | 31.8% | 0.6% | -0.44% | -0.11% | 0.63 | -2.46% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 30 | 50.0% | 0.88% | -0.68% | 0.099% | 1.29 | 2.81% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 21 | 38.1% | 0.58% | -0.35% | 0.002% | 1.01 | -0.01% | -2.37% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 30 | 43.3% | 0.13% | -0.2% | -0.056% | 0.51 | -1.69% | -2.07% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 30 | 53.3% | 0.78% | -0.52% | 0.175% | 1.73 | 5.24% | -5.09% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 30 | 30.0% | 1.64% | -0.77% | -0.044% | 0.92 | -1.71% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 25 | 32.0% | 1.23% | -0.67% | -0.061% | 0.87 | -1.76% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 30 | 50.0% | 1.26% | -0.91% | 0.178% | 1.39 | 5.13% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -0.60%, QQQ -7.03%, TQQQ -23.33%, UPRO -4.20%, SQQQ +18.99%, SPXU +1.19%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 21 | -0.272% | -5.76% |
| EMA 9/21 + volume | 22 | -0.278% | -6.0% |
| Volume spike | 30 | -0.063% | -2.07% |
| EMA 9/21 + volume v2 | 21 | -0.162% | -3.39% |
| CVD turn 3-min (SPY) | 30 | -0.118% | -3.5% |
| CVD turn 3-min (TQQQ) | 30 | -0.007% | -0.33% |
| ORB (no volume filter) | 30 | -0.154% | -4.92% |
| EMA 9/21 (no volume filter) | 25 | -0.187% | -4.82% |
| Volume spike (2x) | 30 | 0.017% | 0.17% |

## Robustness check: 5-minute bars, 2026-09-17 to 2026-11-11 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 35.0% | -0.318% | 0.55 | -6.4% | -11.58% |
| EMA 9/21 + volume | 13 | 46.2% | -0.089% | 0.49 | -1.16% | -1.99% |
| Volume spike | 37 | 35.1% | -0.243% | 0.55 | -8.89% | -16.32% |
| EMA 9/21 + volume v2 | 13 | 46.2% | -0.089% | 0.49 | -1.16% | -1.99% |
| CVD turn 3-min (SPY) | 40 | 52.5% | -0.019% | 0.69 | -0.77% | -1.21% |
| CVD turn 3-min (TQQQ) | 40 | 52.5% | -0.106% | 0.7 | -4.28% | -5.5% |
| ORB (no volume filter) | 40 | 37.5% | -0.081% | 0.84 | -3.59% | -7.02% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.059% | 0.86 | -2.27% | -5.64% |
| Volume spike (2x) | 40 | 37.5% | -0.264% | 0.53 | -10.29% | -16.72% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4202 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4202 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4202 | 6.71% | 30.91% | 1.48% | 3.78% |
| UPRO | 4202 | 3.24% | 21.32% | 0.71% | 1.83% |
| SQQQ | 4202 | 9.97% | 28.94% | 1.52% | 5.02% |
| SPXU | 4202 | 5.71% | 18.8% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 5 trades, $-32.71; SPY 4 trades, $-1.85; SQQQ 2 trades, $+68.75; TQQQ 1 trades, $-9.44; UPRO 5 trades, $-53.62 · exits {'eod': 19, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 4 trades, $-16.36; SPXU 12 trades, $+6.13; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 3 trades, $-17.31 · exits {'eod': 22}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+52.73; SPY 3 trades, $+0.84; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 11 trades, $-27.84 · exits {'eod': 28, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 4 trades, $-16.36; SPXU 9 trades, $+25.28; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.85; UPRO 2 trades, $-12.66 · exits {'eod': 21}
- **CVD turn 3-min (SPY):** SPY 30 trades, $-16.88 · exits {'cvd_sell': 29, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 30 trades, $+52.41 · exits {'cvd_sell': 28, 'stop': 2}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
