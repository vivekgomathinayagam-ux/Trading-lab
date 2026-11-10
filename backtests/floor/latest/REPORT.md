# Trading Floor day-trade lab

Run 2026-11-10T02:19+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-11-09, 28 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 19 | 26.3% | 0.56% | -0.67% | -0.349% | 0.3 | -6.49% | -6.23% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 20 | 35.0% | 0.62% | -0.44% | -0.067% | 0.76 | -1.4% | -3.6% | 0 | loses or too thin after costs |
| Volume spike | yes | 28 | 46.4% | 0.92% | -0.66% | 0.072% | 1.21 | 1.85% | -3.27% | 0 | promising, keep collecting |
| EMA 9/21 + volume v2 | yes | 20 | 40.0% | 0.59% | -0.33% | 0.038% | 1.19 | 0.71% | -2.09% | 0 | loses or too thin after costs |
| CVD turn 3-min (SPY) | yes | 28 | 53.6% | 0.11% | -0.24% | -0.049% | 0.55 | -1.39% | -1.97% | 0 | loses or too thin after costs |
| CVD turn 3-min (TQQQ) | yes | 28 | 60.7% | 0.74% | -0.54% | 0.236% | 2.11 | 6.69% | -2.99% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 28 | 32.1% | 1.64% | -0.71% | 0.046% | 1.1 | 0.93% | -6.64% | 2 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 23 | 30.4% | 1.29% | -0.68% | -0.081% | 0.83 | -2.08% | -5.78% | 1 | loses or too thin after costs |
| Volume spike (2x) | compare | 28 | 50.0% | 1.26% | -0.95% | 0.155% | 1.33 | 4.1% | -5.22% | 1 | promising, keep collecting |

Buy-and-hold over the same window: SPY -1.54%, QQQ -8.59%, TQQQ -27.00%, UPRO -6.76%, SQQQ +25.65%, SPXU +4.11%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 19 | -0.476% | -8.75% |
| EMA 9/21 + volume | 20 | -0.221% | -4.39% |
| Volume spike | 28 | -0.087% | -2.6% |
| EMA 9/21 + volume v2 | 20 | -0.104% | -2.1% |
| CVD turn 3-min (SPY) | 28 | -0.111% | -3.07% |
| CVD turn 3-min (TQQQ) | 28 | 0.045% | 1.15% |
| ORB (no volume filter) | 28 | -0.068% | -2.24% |
| EMA 9/21 (no volume filter) | 23 | -0.206% | -4.87% |
| Volume spike (2x) | 28 | -0.009% | -0.57% |

## Robustness check: 5-minute bars, 2026-09-17 to 2026-11-09 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 20 | 35.0% | -0.181% | 0.69 | -3.78% | -9.62% |
| EMA 9/21 + volume | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| Volume spike | 35 | 45.7% | -0.153% | 0.69 | -5.5% | -13.75% |
| EMA 9/21 + volume v2 | 16 | 43.8% | -0.22% | 0.28 | -3.49% | -4.3% |
| CVD turn 3-min (SPY) | 38 | 55.3% | -0.024% | 0.65 | -0.89% | -1.35% |
| CVD turn 3-min (TQQQ) | 38 | 52.6% | -0.111% | 0.69 | -4.28% | -5.45% |
| ORB (no volume filter) | 38 | 39.5% | -0.014% | 0.97 | -0.94% | -7.01% |
| EMA 9/21 (no volume filter) | 32 | 37.5% | -0.071% | 0.84 | -2.54% | -5.64% |
| Volume spike (2x) | 38 | 42.1% | -0.118% | 0.76 | -4.69% | -12.17% |

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
- **Volume spike:** QQQ 6 trades, $+12.06; SPXU 10 trades, $+54.08; SPY 3 trades, $-4.16; SQQQ 1 trades, $-16.43; UPRO 8 trades, $-27.07 · exits {'eod': 26, 'stop': 2}
- **EMA 9/21 + volume v2:** QQQ 6 trades, $-15.58; SPXU 6 trades, $+30.06; SPY 2 trades, $+1.64; SQQQ 4 trades, $+1.85; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 20}
- **CVD turn 3-min (SPY):** SPY 28 trades, $-13.86 · exits {'cvd_sell': 27, 'stop': 1}
- **CVD turn 3-min (TQQQ):** TQQQ 28 trades, $+66.88 · exits {'cvd_sell': 27, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
