# Trading Floor day-trade lab

Run 2026-10-28T00:34+00:00 · data: Yahoo Finance 1m (archived), 5m, 1d · spec: `strategies/daytrade/spec.md` (pre-registered)

**1-minute backtest window:** 2026-10-01 to 2026-10-27, 19 trading sessions after a 3-session warm-up. Each desk starts with $1,000, trades whole shares, risks 2.5% per trade (stop) to make 5% (target), at most one trade a day, flat by 15:55 ET.

## Results: 1-minute bars (normal slippage)

| Desk | Paper? | Trades | Win rate | Avg win | Avg loss | Expectancy / trade | Profit factor | Total return | Max drawdown | +5% targets hit | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORB + volume | yes | 13 | 38.5% | 0.56% | -0.8% | -0.274% | 0.44 | -3.57% | -3.36% | 0 | loses or too thin after costs |
| EMA 9/21 + volume | yes | 14 | 35.7% | 0.28% | -0.42% | -0.174% | 0.36 | -2.42% | -3.18% | 0 | loses or too thin after costs |
| Volume spike | yes | 19 | 52.6% | 0.96% | -0.7% | 0.177% | 1.54 | 3.27% | -3.24% | 0 | promising, keep collecting |
| ORB (no volume filter) | compare | 19 | 36.8% | 1.31% | -0.84% | -0.049% | 0.91 | -1.16% | -6.64% | 1 | loses or too thin after costs |
| EMA 9/21 (no volume filter) | compare | 16 | 37.5% | 0.7% | -0.57% | -0.094% | 0.73 | -1.58% | -4.26% | 0 | loses or too thin after costs |
| Volume spike (2x) | compare | 19 | 52.6% | 1.04% | -0.88% | 0.132% | 1.32 | 2.38% | -3.24% | 0 | promising, keep collecting |

Buy-and-hold over the same window: SPY +0.70%, QQQ -2.87%, TQQQ -9.94%, UPRO +1.08%, SQQQ +8.49%, SPXU -1.45%

## Same rules, 3x slippage (stress test)

| Desk | Trades | Expectancy / trade | Total return |
|---|---|---|---|
| ORB + volume | 13 | -0.406% | -5.22% |
| EMA 9/21 + volume | 14 | -0.343% | -4.73% |
| Volume spike | 19 | -0.025% | -0.63% |
| ORB (no volume filter) | 19 | -0.166% | -3.35% |
| EMA 9/21 (no volume filter) | 16 | -0.228% | -3.67% |
| Volume spike (2x) | 19 | -0.04% | -0.91% |

## Robustness check: 5-minute bars, 2026-09-03 to 2026-10-27 (38 sessions)

| Desk | Trades | Win rate | Expectancy / trade | Profit factor | Total return | Max drawdown |
|---|---|---|---|---|---|---|
| ORB + volume | 19 | 42.1% | -0.516% | 0.22 | -9.45% | -8.74% |
| EMA 9/21 + volume | 13 | 46.2% | -0.11% | 0.39 | -1.43% | -1.59% |
| Volume spike | 35 | 25.7% | -0.533% | 0.15 | -17.17% | -15.04% |
| ORB (no volume filter) | 38 | 42.1% | -0.117% | 0.74 | -4.65% | -7.03% |
| EMA 9/21 (no volume filter) | 33 | 39.4% | -0.034% | 0.89 | -1.27% | -4.2% |
| Volume spike (2x) | 38 | 36.8% | -0.37% | 0.34 | -13.3% | -11.96% |

## How realistic is +5% in one day? (daily bars since 2010)

| ETF | Days | Reached +5% above the open | Fell 2.5% below the open | Both on the same day | Closed +5% above the open |
|---|---|---|---|---|---|
| SPY | 4191 | 0.17% | 1.67% | 0.05% | 0.02% |
| QQQ | 4191 | 0.19% | 3.63% | 0.07% | 0.1% |
| TQQQ | 4191 | 6.68% | 30.92% | 1.48% | 3.77% |
| UPRO | 4191 | 3.22% | 21.31% | 0.72% | 1.84% |
| SQQQ | 4191 | 9.93% | 28.9% | 1.53% | 4.99% |
| SPXU | 4191 | 5.7% | 18.78% | 0.69% | 2.77% |

## Per-ETF breakdown (1-minute, paper desks)

- **ORB + volume:** QQQ 2 trades, $+1.26; SPXU 4 trades, $-18.63; SPY 3 trades, $-0.87; SQQQ 1 trades, $+21.67; TQQQ 1 trades, $-9.44; UPRO 2 trades, $-29.63 · exits {'eod': 12, 'stop': 1}
- **EMA 9/21 + volume:** QQQ 1 trades, $-1.71; SPXU 9 trades, $-16.22; SPY 2 trades, $+4.53; TQQQ 1 trades, $-0.79; UPRO 1 trades, $-10.07 · exits {'eod': 14}
- **Volume spike:** QQQ 2 trades, $+4.32; SPXU 8 trades, $+20.39; SPY 1 trades, $-2.06; SQQQ 1 trades, $-16.43; TQQQ 1 trades, $+18.34; UPRO 6 trades, $+8.13 · exits {'eod': 18, 'stop': 1}

## How to read this
- About 20 sessions gives each desk at most about 20 trades. That's enough to spot a broken rule, not enough to prove an edge. The gate for live is 50+ trades over 4+ weeks. The 1-minute archive grows every trading day, so each run has more history.
- Paper trading runs these exact desks (same code) on live bars, whatever this report says.
