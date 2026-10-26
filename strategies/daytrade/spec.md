# Day-trade desks on the Trading Floor (pre-registered 2026-10-25)

Requested by Vivek on 2026-10-25: keep paper trading ORB and the 9/21 EMA cross; focus on TQQQ and the
other leveraged and inverse ETFs for SPY and QQQ; for every day-trade setup, use 1-minute volume to spot
potential big moves; target +5% on every trade and let it compound; backtest now, and paper trade
regardless of the backtest result, without stopping.

These rules were written down **before** any backtest ran. Changing them later counts as a new variant
and must be reported as one.

## Instruments
SPY, QQQ (1x) · TQQQ, UPRO (3x long QQQ / S&P 500) · SQQQ, SPXU (3x inverse).
Long only. Bearish days are traded by **buying** an inverse ETF, never by shorting (money rule 4).

## Rules shared by every desk
| Item | Rule |
|---|---|
| Session | Regular hours only. New entries 09:35-15:30 ET. Flat by 15:55 ET; nothing is held overnight. |
| Target | **+5% from the entry price** (Vivek's rule). |
| Stop | **-2.5% from the entry price** (half the target, so a win pays 2x a loss). |
| Same-bar tie | If one bar touches both the stop and the target, the stop counts (conservative). |
| Fills | Signal at a bar's close; entry at the next bar's open. Gaps through a stop fill at the open. |
| Frequency | At most **one entry per desk per day**. A $1,000 cash account can't reuse sale proceeds the same day (settlement). |
| Sizing | All of the desk's cash in whole shares, no margin. At a 2.5% stop that risks about 2.5% of equity, under the 5% cap. Profits and losses compound. |
| Costs | Slippage per side: 0.02% on SPY/QQQ, 0.05% on 3x ETFs. A stress test triples both. No commissions (Tradier/Robinhood ETF trades are free). |
| One position | Each desk holds one position at a time across all six ETFs. If several signal on the same minute, the order is SPY, QQQ, TQQQ, UPRO, SQQQ, SPXU. |

## 1-minute volume confirmation ("volume spike")
A 1-minute bar is a spike when **both** hold:
1. Its volume is at least **3x the median volume of the previous 20 one-minute bars**, and
2. Its volume is at least **1.5x the average volume of the same minute over the previous 5 sessions** (this stops the opening minutes from always looking like spikes). Skipped until 3 sessions of history exist.

## The desks
| Desk | Entry signal (at a bar's close) |
|---|---|
| **ORB + volume** | After the 09:30-09:45 opening range, the close crosses above the range high on a volume-spike bar. |
| **EMA 9/21 + volume** | On 5-minute closes (built from 1-minute bars), EMA 9 crosses above EMA 21, and one of that 5-minute bucket's 1-minute bars is a volume spike. From 09:45. |
| **Volume spike** | A volume-spike bar closes up (close > open), above VWAP, and above the high of the previous 15 bars. |

Comparisons, backtest only (not paper traded): ORB with no volume filter, EMA 9/21 with no volume filter,
and Volume spike at 2x instead of 3x. 6 rules in total, all reported.

## Honest limits, stated before results
- **Free 1-minute history covers only about the last 30 days** (Yahoo). That's roughly 20 sessions, so each
  desk gets at most about 20 trades. Far too few to prove an edge. The lab archives every day's 1-minute
  bars to branch `data`, so each later run has more history.
- A robustness check reruns the same rules on 5-minute bars over 60 days.
- A +5% move within one day is rare for 1x ETFs. The lab measures how often each ETF reached +5% above its
  open since 2010, so the target can be judged on its own.

## Paper trading
The Railway bot runs the same code (`strategies/daytrade/core.py`) on live 1-minute bars, one virtual
$1,000 book per desk. It places paper orders on the Tradier sandbox, and **judges results on shadow fills
at real-time prices**, because the sandbox is 15 minutes delayed. It keeps going on days with no signal and
never stops on its own. Only the risk engine's caps can stop it.

## Gate (unchanged)
Live-ready needs 50+ trades over 4+ weeks, positive expectancy after costs, profit factor 1.2+, max
drawdown 20% or less, better risk-adjusted return than SPY buy-and-hold, and paper close to backtest.
