# Trading Floor day-trade lab

Run 2026-11-03T02:58+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-02, 23 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 16 | 37.5% | 1.29% | -0.66% | 0.067% | 1.16 | 0.9% | -3.54% | 1 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 16 | 31.2% | 0.79% | -0.44% | -0.057% | 0.81 | -0.98% | -4.2% | 0 | loses or too thin after costs |
| Volume spike | yes | 23 | 52.2% | 0.9% | -0.81% | 0.082% | 1.21 | 1.73% | -3.24% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 15 | 40.0% | 0.73% | -0.32% | 0.1% | 1.52 | 1.47% | -2.37% | 0 | promising, keep collecting |
| CVD turn 3-min (SPY) | yes | 23 | 34.8% | 0.13% | -0.09% | -0.009% | 0.84 | -0.21% | -0.48% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 23 | 60.9% | 0.84% | -0.15% | 0.453% | 8.67 | 10.89% | -0.83% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 23 | 30.4% | 1.31% | -0.8% | -0.155% | 0.72 | -3.74% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 19 | 36.8% | 1.29% | -0.61% | 0.092% | 1.24 | 1.55% | -5.78% | 1 | promising, keep collecting |
| Volume spike (2x) | compare | 23 | 47.8% | 1.03% | -1.04% | -0.049% | 0.91 | -1.32% | -3.62% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY -1.60%, QQQ -8.28%, TQQQ -24.63%, UPRO -5.95%, SQQQ +27.93%, SPXU +5.70%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 16 | -0.07% | -1.3% |
| EMA 9/21 + volume | 16 | -0.241% | -3.85% |
| Volume spike | 23 | -0.097% | -2.38% |
| EMA 9/21 + volume v2 | 15 | -0.075% | -1.17% |
| CVD turn 3-min (SPY) | 23 | -0.071% | -1.62% |
| CVD turn 3-min (TQQQ) | 23 | 0.263% | 6.18% |
| ORB (no volume filter) | 23 | -0.272% | -6.3% |
| EMA 9/21 (no volume filter) | 19 | -0.046% | -1.08% |
| Volume spike (2x) | 23 | -0.208% | -4.86% |

## Robustness check: 5-minute bars, 2026-09-11 to 2026-11-02 (37 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 36.8% | -0.442% | 0.35 | -8.2% | -11.51% |
| EMA 9/21 + volume | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| Volume spike | 34 | 29.4% | -0.447% | 0.3 | -14.3% | -17.23% |
| EMA 9/21 + volume v2 | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| CVD turn 3-min (SPY) | 37 | 51.4% | -0.005% | 0.88 | -0.18% | -0.69% |
| CVD turn 3-min (TQQQ) | 37 | 48.6% | -0.117% | 0.66 | -4.36% | -4.78% |
| ORB (no volume filter) | 37 | 40.5% | -0.132% | 0.72 | -5.03% | -7.03% |
| EMA 9/21 (no volume filter) | 32 | 43.8% | 0.096% | 1.28 | 2.85% | -5.72% |
| Volume spike (2x) | 37 | 35.1% | -0.397% | 0.33 | -13.85% | -15.11% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4196 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4196 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4196 | 6.67% | 30.93% | 1.48% | 3.77% |
| UPRO | 4196 | 3.22% | 21.33% | 0.71% | 1.84% |
| SQQQ | 4196 | 9.96% | 28.88% | 1.53% | 5.0% |
| SPXU | 4196 | 5.7% | 18.76% | 0.69% | 2.76% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 4 trades, $-1.85; SQQQ 2 trades, $+68.75; TQQQ 1 trades, $-9.44; UPRO 3 trades, $-31.12 · exits {'eod': 14, 'stop': 1, 'target': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 11 trades, $+4.78; SPY 1 trades, $+2.66; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.72 · exits {'eod': 16}
- **Volume spike:** QQQ 3 trades, $+6.61; SPXU 9 trades, $+29.94; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 8 trades, $-19.06 · exits {'eod': 21, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 1 trades, $-1.71; SPXU 8 trades, $+23.88; SPY 1 trades, $+2.66; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.85; UPRO 1 trades, $-10.07 · exits {'eod': 15}
- **CVD turn 3-min (SPY):** SPY 23 trades, $-2.07 · exits {'cvd_sell': 23}
- **CVD turn 3-min (TQQQ):** TQQQ 23 trades, $+108.94 · exits {'cvd_sell': 23}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
