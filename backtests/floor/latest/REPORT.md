# Trading Floor day-trade lab

Run 2026-11-12T02:22+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-11, 30 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 21 | 28.6% | 0.47% | -0.73% | -0.383% | 0.26 | -7.83% | -7.59% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 22 | 36.4% | 0.56% | -0.43% | -0.074% | 0.73 | -1.68% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 30 | 43.3% | 0.92% | -0.59% | 0.06% | 1.18 | 1.62% | -3.27% | 0 | loses or too thin after costs |
| EMA 9/21 + volume v2 | yes | 22 | 40.9% | 0.54% | -0.34% | 0.022% | 1.11 | 0.43% | -2.09% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 30 | 53.3% | 0.12% | -0.22% | -0.041% | 0.61 | -1.24% | -1.97% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 30 | 53.3% | 0.78% | -0.62% | 0.126% | 1.43 | 3.68% | -5.17% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 30 | 30.0% | 1.64% | -0.77% | -0.044% | 0.92 | -1.7% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 25 | 32.0% | 1.23% | -0.67% | -0.06% | 0.87 | -1.73% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 30 | 46.7% | 1.26% | -0.83% | 0.143% | 1.32 | 4.03% | -5.22% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -0.60%, QQQ -7.03%, TQQQ -23.33%, UPRO -4.20%, SQQQ +18.99%, SPXU +1.16%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 21 | -0.51% | -10.25% |
| EMA 9/21 + volume | 22 | -0.226% | -4.92% |
| Volume spike | 30 | -0.097% | -3.07% |
| EMA 9/21 + volume v2 | 22 | -0.119% | -2.63% |
| CVD turn 3-min (SPY) | 30 | -0.102% | -3.04% |
| CVD turn 3-min (TQQQ) | 30 | -0.062% | -1.99% |
| ORB (no volume filter) | 30 | -0.154% | -4.91% |
| EMA 9/21 (no volume filter) | 25 | -0.186% | -4.79% |
| Volume spike (2x) | 30 | -0.019% | -0.89% |

## Robustness check: 5-minute bars, 2026-09-17 to 2026-11-11 (40 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 21 | 38.1% | -0.17% | 0.7 | -3.73% | -9.62% |
| EMA 9/21 + volume | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| Volume spike | 37 | 45.9% | -0.14% | 0.71 | -5.35% | -13.75% |
| EMA 9/21 + volume v2 | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| CVD turn 3-min (SPY) | 40 | 55.0% | -0.023% | 0.66 | -0.91% | -1.35% |
| CVD turn 3-min (TQQQ) | 40 | 52.5% | -0.118% | 0.67 | -4.74% | -5.56% |
| ORB (no volume filter) | 40 | 37.5% | -0.077% | 0.85 | -3.46% | -7.01% |
| EMA 9/21 (no volume filter) | 34 | 38.2% | -0.056% | 0.87 | -2.18% | -5.64% |
| Volume spike (2x) | 40 | 42.5% | -0.131% | 0.74 | -5.43% | -12.17% |

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

- **ORB + volume:** QQQ 5 trades, $-1.32; SPXU 5 trades, $-32.03; SPY 5 trades, $-9.24; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 4 trades, $-47.88 · exits {'eod': 20, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 6 trades, $-16.57; SPXU 10 trades, $+12.31; SPY 2 trades, $+1.64; SQQQ 1 trades, $+1.05; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.48 · exits {'eod': 22}
- **Volume spike:** QQQ 7 trades, $+11.68; SPXU 10 trades, $+54.08; SPY 3 trades, $-4.16; SQQQ 1 trades, $-16.43; UPRO 9 trades, $-28.94 · exits {'eod': 28, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 7 trades, $-19.78; SPXU 7 trades, $+31.46; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 22}
- **CVD turn 3-min (SPY):** SPY 30 trades, $-12.36 · exits {'cvd_sell': 29, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 30 trades, $+36.78 · exits {'cvd_sell': 28, 'stop': 2}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
