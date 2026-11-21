# Payoff Ratio and Expectancy From Average Win and Average Loss (free table, in dollars)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

Two numbers from any trade journal tell you most of the story: your win rate and your payoff ratio (average winning trade divided by average losing trade). Expectancy per trade in dollars is: win rate x average win - loss rate x average loss.

## Table: expectancy per trade in dollars

| Win rate | Avg win $150, avg loss $100 (payoff 1.5) | Avg win $100, avg loss $100 (payoff 1.0) | Avg win $75, avg loss $100 (payoff 0.75) |
|---|---|---|---|
| 30% | -25.00 | -40.00 | -47.50 |
| 40% | 0.00 | -20.00 | -30.00 |
| 50% | +25.00 | 0.00 | -12.50 |
| 60% | +50.00 | +20.00 | +5.00 |
| 70% | +75.00 | +40.00 | +22.50 |

Break-even win rate = average loss / (average win + average loss): 40% at payoff 1.5, 50% at payoff 1.0, about 57.1% at payoff 0.75.

## Worked example (hand-checked)
Win rate 60%, average win $75, average loss $100: 0.60 x 75 - 0.40 x 100 = 45 - 40 = +$5 per trade, before commissions. A 60% win rate with small winners and larger losers barely clears break-even, and commissions can erase it.

## How to read it
- A high win rate does not guarantee positive expectancy; the payoff ratio decides where break-even sits.
- Subtract commissions and fees per round trip from every cell; see the break-even-with-fees page.
- These are averages over a sample. With few trades the true values are uncertain; see the confidence-interval page.

## Related free pages
- [Breakeven win rate by reward-to-risk](breakeven-win-rate-by-reward-to-risk.md)
- [Expected value per trade in R](expected-value-per-trade-in-r.md)
- [How many trades to trust a win rate](how-many-trades-to-trust-a-win-rate.md)
- [Options break-even with commissions](options-breakeven-with-fees.md)

## Want it in a spreadsheet?
The Trader Toolkit ($12, Gumroad) has a trade journal with win rate, average win/loss, expectancy, profit factor, drawdown and streaks, plus an options risk and position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance; no results claims.
