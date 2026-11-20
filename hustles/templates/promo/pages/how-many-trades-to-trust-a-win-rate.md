# How Many Trades Before You Can Trust Your Win Rate? (free confidence-interval table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

A journal with 20 trades and a 60% win rate does not prove the true rate is 60%. The sample is small, so the true rate could be well above or below it. This page shows how wide that uncertainty is, using the Wilson 95% confidence interval for a win rate.

## Table: 95% range for the true win rate (percent)

| Trades in journal | Observed 40% | Observed 50% | Observed 60% |
|---|---|---|---|
| 20 | 22 to 61 | 30 to 70 | 39 to 78 |
| 30 | 25 to 58 | 33 to 67 | 42 to 75 |
| 50 | 28 to 54 | 37 to 63 | 46 to 72 |
| 100 | 31 to 50 | 40 to 60 | 50 to 69 |
| 200 | 33 to 47 | 43 to 57 | 53 to 67 |
| 500 | 36 to 44 | 46 to 54 | 56 to 64 |

Read across: 50 trades with 60% wins is consistent with a true win rate anywhere from about 46% to 72%.

## How to read it

- With 20 trades, a "60% win rate" and a "40% win rate" journal have overlapping ranges (39 to 61 is shared). You cannot tell them apart yet.
- The range shrinks roughly with the square root of the number of trades: four times the trades, about half the width.
- Compare the low end of the range with your break-even win rate (`1 / (1 + reward-to-risk)`; see the breakeven page below). If the low end sits under break-even, the journal has not shown an edge yet.
- This covers win rate only. Average win and average loss are uncertain too, and so is expectancy per trade in R.

## Method

Wilson score interval, z = 1.96: center = (p + z²/2n) / (1 + z²/n), half-width = z·sqrt(p(1-p)/n + z²/4n²) / (1 + z²/n). Table computed by script; the 50-trade, 60% cell was hand-checked (46 to 72). It assumes trades are independent and similar, which real trading often is not.

## Related free pages
- [Breakeven win rate by reward-to-risk](breakeven-win-rate-by-reward-to-risk.md)
- [Expected value per trade in R](expected-value-per-trade-in-r.md)
- [Losing streak probability table](losing-streak-probability-table.md)

## Want it in a spreadsheet?
The Trader Toolkit ($12, Gumroad) has a trade journal with win rate, expectancy, profit factor, drawdown and streaks, plus an options risk and position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance; no results claims.
