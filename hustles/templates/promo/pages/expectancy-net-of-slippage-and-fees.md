# How Much Slippage Erases a Trading Edge? Expectancy Net of Slippage (free table)

Slippage and commissions are paid on every trade, win or lose, so they come off expectancy one-for-one. This table subtracts a fixed per-trade cost, measured in R (1R = the amount you risk on the trade), from gross expectancy. Arithmetic only: not advice, not a signal, no prediction of results. Options involve risk of loss.

## The formula
Gross expectancy (R) = win rate x reward:risk - (1 - win rate)
Net expectancy (R) = gross expectancy - slippage and fees per trade (in R)

Example: a 45% win rate at 2:1 has gross expectancy 0.45 x 2 - 0.55 = +0.35R. If each round trip costs 0.15R in bid-ask slippage and fees, net expectancy is +0.20R. At 0.35R of cost the edge is gone.

## Table
| Win rate | Reward:risk | Gross expectancy (R) | Net at 0.05R slip | Net at 0.10R | Net at 0.15R | Net at 0.20R | Slippage that erases it (R) |
|---|---|---|---|---|---|---|---|
| 35% | 1:1 | -0.30 | -0.35 | -0.40 | -0.45 | -0.50 | 0.00 |
| 35% | 1.5:1 | -0.13 | -0.18 | -0.23 | -0.28 | -0.33 | 0.00 |
| 35% | 2:1 | +0.05 | -0.00 | -0.05 | -0.10 | -0.15 | 0.05 |
| 35% | 3:1 | +0.40 | +0.35 | +0.30 | +0.25 | +0.20 | 0.40 |
| 40% | 1:1 | -0.20 | -0.25 | -0.30 | -0.35 | -0.40 | 0.00 |
| 40% | 1.5:1 | +0.00 | -0.05 | -0.10 | -0.15 | -0.20 | 0.00 |
| 40% | 2:1 | +0.20 | +0.15 | +0.10 | +0.05 | +0.00 | 0.20 |
| 40% | 3:1 | +0.60 | +0.55 | +0.50 | +0.45 | +0.40 | 0.60 |
| 45% | 1:1 | -0.10 | -0.15 | -0.20 | -0.25 | -0.30 | 0.00 |
| 45% | 1.5:1 | +0.12 | +0.07 | +0.02 | -0.02 | -0.08 | 0.12 |
| 45% | 2:1 | +0.35 | +0.30 | +0.25 | +0.20 | +0.15 | 0.35 |
| 45% | 3:1 | +0.80 | +0.75 | +0.70 | +0.65 | +0.60 | 0.80 |
| 50% | 1:1 | +0.00 | -0.05 | -0.10 | -0.15 | -0.20 | 0.00 |
| 50% | 1.5:1 | +0.25 | +0.20 | +0.15 | +0.10 | +0.05 | 0.25 |
| 50% | 2:1 | +0.50 | +0.45 | +0.40 | +0.35 | +0.30 | 0.50 |
| 50% | 3:1 | +1.00 | +0.95 | +0.90 | +0.85 | +0.80 | 1.00 |
| 55% | 1:1 | +0.10 | +0.05 | +0.00 | -0.05 | -0.10 | 0.10 |
| 55% | 1.5:1 | +0.38 | +0.33 | +0.28 | +0.23 | +0.18 | 0.38 |
| 55% | 2:1 | +0.65 | +0.60 | +0.55 | +0.50 | +0.45 | 0.65 |
| 55% | 3:1 | +1.20 | +1.15 | +1.10 | +1.05 | +1.00 | 1.20 |
| 60% | 1:1 | +0.20 | +0.15 | +0.10 | +0.05 | -0.00 | 0.20 |
| 60% | 1.5:1 | +0.50 | +0.45 | +0.40 | +0.35 | +0.30 | 0.50 |
| 60% | 2:1 | +0.80 | +0.75 | +0.70 | +0.65 | +0.60 | 0.80 |
| 60% | 3:1 | +1.40 | +1.35 | +1.30 | +1.25 | +1.20 | 1.40 |

## Turning dollars into R
Slippage in R = (round-trip slippage + fees in dollars) / (dollars risked on the trade). On an option you buy at the ask and sell at the bid, a $0.10 wide quote on a 1-contract trade costs about $10 round trip before commissions. If you risk $100, that is 0.10R; if you risk $50, it is 0.20R. The same quote costs a smaller account more, in R, which is why tight stops and thin options are hard to make work.

## How to use it
1. Pull your average win rate and average reward:risk from your journal (at least a few dozen trades; see the page on how many trades to trust a win rate).
2. Estimate your average round-trip cost in dollars (spread you actually paid plus commissions) and divide by your average dollars risked.
3. If net expectancy is near zero, the problem is cost per trade, not entry timing.

## Want it in a spreadsheet?
The Trader Toolkit ($12, Gumroad) has a trade journal that records fees and R for every trade and shows expectancy, drawdown and streaks, plus an options risk and position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance (Claude); no results claims.

Table computed by script; spot checks: 50% at 1:1 = 0.00R gross; 40% at 3:1 = +0.60R gross, +0.45R after 0.15R.
