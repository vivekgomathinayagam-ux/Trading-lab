# Trading Floor day-trade lab

Run 2026-11-18T02:58+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-17, 34 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 23 | 34.8% | 1.17% | -0.73% | -0.071% | 0.85 | -1.85% | -4.28% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 24 | 29.2% | 0.6% | -0.54% | -0.206% | 0.46 | -4.9% | -5.48% | 0 | loses or too thin after costs |
| Volume spike | yes | 34 | 52.9% | 1.02% | -0.65% | 0.234% | 1.76 | 8.01% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 23 | 34.8% | 0.58% | -0.49% | -0.119% | 0.63 | -2.76% | -4.17% | 0 | loses or too thin after costs |
| ORB (no volume filter) | compare | 34 | 35.3% | 1.71% | -0.74% | 0.123% | 1.26 | 3.8% | -6.64% | 2 | promising, keep collecting |
| EMA 9/21 (no volume filter) | compare | 28 | 32.1% | 1.14% | -0.63% | -0.064% | 0.85 | -2.03% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 34 | 52.9% | 1.34% | -0.86% | 0.305% | 1.75 | 10.48% | -4.73% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -4.18%, QQQ -11.52%, TQQQ -34.24%, UPRO -14.48%, SQQQ +37.68%, SPXU +12.93%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 23 | -0.215% | -5.05% |
| EMA 9/21 + volume | 24 | -0.376% | -8.73% |
| Volume spike | 34 | 0.068% | 2.09% |
| EMA 9/21 + volume v2 | 23 | -0.275% | -6.2% |
| ORB (no volume filter) | 34 | 0.006% | -0.26% |
| EMA 9/21 (no volume filter) | 28 | -0.184% | -5.26% |
| Volume spike (2x) | 34 | 0.143% | 4.58% |

## Robustness check: 5-minute bars, 2026-09-24 to 2026-11-17 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 31.6% | -0.338% | 0.54 | -6.46% | -9.96% |
| EMA 9/21 + volume | 12 | 41.7% | -0.111% | 0.41 | -1.34% | -2.0% |
| Volume spike | 36 | 38.9% | -0.155% | 0.72 | -5.73% | -16.2% |
| EMA 9/21 + volume v2 | 12 | 41.7% | -0.111% | 0.41 | -1.34% | -2.0% |
| ORB (no volume filter) | 39 | 38.5% | 0.108% | 1.22 | 3.71% | -7.04% |
| EMA 9/21 (no volume filter) | 33 | 39.4% | -0.068% | 0.84 | -2.5% | -5.64% |
| Volume spike (2x) | 39 | 35.9% | -0.27% | 0.55 | -10.28% | -16.84% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4207 | 0.17% | 1.69% | 0.05% | 0.02% |
| QQQ | 4207 | 0.19% | 3.64% | 0.07% | 0.1% |
| TQQQ | 4207 | 6.73% | 30.95% | 1.47% | 3.78% |
| UPRO | 4207 | 3.23% | 21.37% | 0.71% | 1.83% |
| SQQQ | 4207 | 10.01% | 28.95% | 1.52% | 5.02% |
| SPXU | 4207 | 5.7% | 18.8% | 0.69% | 2.78% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 4 trades, $-0.82; SPXU 5 trades, $-32.57; SPY 4 trades, $-1.85; SQQQ 3 trades, $+84.28; TQQQ 2 trades, $-13.92; UPRO 5 trades, $-53.62 · exits {'eod': 21, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 4 trades, $-16.36; SPXU 12 trades, $+6.28; SPY 1 trades, $+2.66; SQQQ 1 trades, $+1.05; TQQQ 2 trades, $-11.07; UPRO 4 trades, $-31.60 · exits {'eod': 24}
- **Volume spike:** QQQ 4 trades, $+0.51; SPXU 10 trades, $+57.74; SPY 4 trades, $-1.10; SQQQ 3 trades, $+13.90; TQQQ 2 trades, $+36.93; UPRO 11 trades, $-27.84 · exits {'eod': 32, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 4 trades, $-16.36; SPXU 9 trades, $+25.28; SPY 1 trades, $+2.66; SQQQ 4 trades, $+1.85; TQQQ 2 trades, $-11.71; UPRO 3 trades, $-29.33 · exits {'eod': 23}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
