# Trading Floor day-trade lab

Run 2026-10-29T22:17+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-29, 21 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 15 | 33.3% | 0.56% | -0.66% | -0.254% | 0.43 | -3.81% | -3.54% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 16 | 31.2% | 0.28% | -0.44% | -0.217% | 0.28 | -3.45% | -4.19% | 0 | loses or too thin after costs |
| Volume spike | yes | 21 | 52.4% | 0.9% | -0.64% | 0.164% | 1.54 | 3.35% | -3.24% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 15 | 40.0% | 0.31% | -0.32% | -0.067% | 0.65 | -1.01% | -2.37% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 21 | 38.1% | 0.13% | -0.09% | -0.005% | 0.91 | -0.11% | -0.48% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 21 | 61.9% | 0.78% | -0.12% | 0.44% | 10.73 | 9.6% | -0.83% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 21 | 33.3% | 1.31% | -0.8% | -0.098% | 0.82 | -2.27% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 18 | 33.3% | 0.7% | -0.61% | -0.172% | 0.57 | -3.15% | -5.78% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 21 | 47.6% | 1.04% | -0.9% | 0.024% | 1.05 | 0.32% | -3.24% | 0 | loses or too thin after costs |

Buy-and-hold over the same window: SPY +0.68%, QQQ -3.68%, TQQQ -12.24%, UPRO +0.96%, SQQQ +11.13%, SPXU -1.24%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 15 | -0.386% | -5.71% |
| EMA 9/21 + volume | 16 | -0.392% | -6.12% |
| Volume spike | 21 | -0.03% | -0.78% |
| EMA 9/21 + volume v2 | 15 | -0.237% | -3.51% |
| CVD turn 3-min (SPY) | 21 | -0.067% | -1.41% |
| CVD turn 3-min (TQQQ) | 21 | 0.251% | 5.37% |
| ORB (no volume filter) | 21 | -0.218% | -4.71% |
| EMA 9/21 (no volume filter) | 18 | -0.308% | -5.49% |
| Volume spike (2x) | 21 | -0.15% | -3.27% |

## Robustness check: 5-minute bars, 2026-09-04 to 2026-10-29 (39 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 40.0% | -0.378% | 0.27 | -7.36% | -8.95% |
| EMA 9/21 + volume | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| Volume spike | 36 | 25.0% | -0.481% | 0.16 | -16.04% | -15.94% |
| EMA 9/21 + volume v2 | 14 | 42.9% | -0.144% | 0.31 | -2.0% | -2.17% |
| CVD turn 3-min (SPY) | 39 | 53.8% | -0.003% | 0.93 | -0.11% | -0.77% |
| CVD turn 3-min (TQQQ) | 39 | 48.7% | -0.062% | 0.77 | -2.45% | -5.0% |
| ORB (no volume filter) | 39 | 41.0% | -0.094% | 0.78 | -3.88% | -7.06% |
| EMA 9/21 (no volume filter) | 35 | 37.1% | -0.078% | 0.77 | -2.83% | -5.72% |
| Volume spike (2x) | 39 | 35.9% | -0.323% | 0.37 | -12.0% | -12.71% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4194 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4194 | 0.19% | 3.62% | 0.07% | 0.1% |
| TQQQ | 4194 | 6.68% | 30.9% | 1.48% | 3.77% |
| UPRO | 4194 | 3.22% | 21.29% | 0.72% | 1.84% |
| SQQQ | 4194 | 9.92% | 28.9% | 1.53% | 4.98% |
| SPXU | 4194 | 5.7% | 18.76% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 4 trades, $-1.85; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 3 trades, $-31.12 · exits {'eod': 14, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 10 trades, $-21.79; SPY 2 trades, $+4.53; TQQQ 1 trades, $-0.79; UPRO 2 trades, $-14.72 · exits {'eod': 16}
- **Volume spike:** QQQ 3 trades, $+6.61; SPXU 8 trades, $+20.39; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 7 trades, $+6.64 · exits {'eod': 20, 'stop': 1}
- **EMA 9/21 + volume v2:** QQQ 1 trades, $-1.71; SPXU 7 trades, $-2.72; SPY 2 trades, $+4.53; SQQQ 3 trades, $+0.75; TQQQ 1 trades, $-0.85; UPRO 1 trades, $-10.07 · exits {'eod': 15}
- **CVD turn 3-min (SPY):** SPY 21 trades, $-1.12 · exits {'cvd_sell': 21}
- **CVD turn 3-min (TQQQ):** TQQQ 21 trades, $+96.05 · exits {'cvd_sell': 21}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
