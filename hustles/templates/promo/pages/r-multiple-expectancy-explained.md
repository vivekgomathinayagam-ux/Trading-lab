# R-Multiples and Expectancy for an Options Trade Journal: Worked Example (free)

Arithmetic only. Not advice, not a signal. The trades below are made-up numbers, not real results, and say nothing about what any strategy earns. Options involve risk of loss.

## Definitions

- **1R** = the dollars you decided to risk on a trade before entering (for a defined-risk option trade, usually its max loss).
- **R-multiple** of a trade = profit or loss in dollars / 1R. A trade that lost exactly its planned risk is -1R; one that made twice its risk is +2R.
- **Win rate** = winning trades / all trades.
- **Average win / average loss** = mean R of winners / mean R of losers.
- **Expectancy** (per trade, in R) = win rate x average win - loss rate x average loss. It is also just the mean of all R-multiples.
- **Profit factor** = total R won / total R lost.

## Worked example: 10 made-up trades

R-multiples: +2.0, -1.0, -1.0, +1.5, -1.0, +3.0, -1.0, -0.5, +2.0, -1.0

- Trades 10, winners 4, losers 6. Win rate = 4/10 = **40%**
- Sum = **+3.0R**; expectancy = 3.0 / 10 = **+0.30R per trade**
- Average win = (2.0 + 1.5 + 3.0 + 2.0) / 4 = **2.125R**; average loss = 5.5 / 6 = **0.917R**
- Check with the formula: 0.40 x 2.125 - 0.60 x 0.917 = **0.30R** (matches)
- Profit factor = 8.5 / 5.5 = **1.55**
- If 1R was $50: total = $150, expectancy = $15 per trade.

A 40% win rate can still have positive expectancy, and a 70% win rate can have negative expectancy if the losers are large. That is why a journal should log R, not just win or loss.

## Caution about sample size

Ten trades say almost nothing. Expectancy from a small sample swings widely; keep logging before reading anything into it. Count fees and slippage in your R.

## What a journal sheet should record per trade

Date, symbol, structure (long call, bull put spread, etc.), planned max loss (1R), entry and exit, fees, result in dollars, R-multiple, and a one-line note on whether you followed your plan.

## Want it automated?

The **Trader Toolkit** ($12, built with AI assistance) has a trade journal that calculates win rate, expectancy, profit factor, drawdown and streaks from your entries, plus a risk and position-size calculator and a trading-plan checklist pack: https://vivekgo8.gumroad.com/l/aobhdm
