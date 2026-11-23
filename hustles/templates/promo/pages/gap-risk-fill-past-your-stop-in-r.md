# Gap Risk: How Much Does a Fill Past Your Stop Cost in R? (free table)

A stop order is a trigger, not a guaranteed price. If the market gaps or moves fast, you can be filled beyond your stop, and the loss is bigger than the 1R you planned. This table shows the actual loss in R (1R = the loss you planned at the stop) when you are filled a given percent past the stop. Arithmetic only: not advice, not a signal, no prediction of results. Options involve risk of loss.

## The formula
Loss in R = (stop distance % + extra % past the stop) / stop distance %

Example: a 2% stop filled 3% past the stop is a 5% loss, which is 5 / 2 = 2.50R.

## Table
| Stop distance (% of entry price) | Fill 0.5% past stop | Fill 1% past stop | Fill 2% past stop | Fill 3% past stop | Fill 5% past stop |
|---|---|---|---|---|---|
| 0.5% | 2.00R | 3.00R | 5.00R | 7.00R | 11.00R |
| 1% | 1.50R | 2.00R | 3.00R | 4.00R | 6.00R |
| 2% | 1.25R | 1.50R | 2.00R | 2.50R | 3.50R |
| 3% | 1.17R | 1.33R | 1.67R | 2.00R | 2.67R |
| 5% | 1.10R | 1.20R | 1.40R | 1.60R | 2.00R |

Tight stops are hit hardest: a 0.5% stop filled 1% past it loses 3.00R, while a 5% stop with the same 1% overshoot loses 1.20R.

## Worked example in dollars
Account $10,000, risk 1% ($100) per trade, 2% stop on the underlying. Position size = $100 / 0.02 = $5,000. If the fill comes 3% past the stop, the loss is $5,000 x 5% = $250, or 2.50R and 2.5% of the account instead of 1%.

## Sizing for the gap you can't control
If you want a gap of 3% past your stop to cost no more than 1% of the account ($100), the position can be at most $100 / 0.05 = $2,000 at that stop distance, not $5,000. Defined-risk positions (a long option or a vertical spread) cap the loss at the premium paid or the spread width, so their worst case is known before entry: see the vertical spread max-loss page.

## How to use it
1. Look at your largest losses in your journal. Any loss over 1.5R usually means a stop was filled past its level.
2. Decide how large an overshoot you want to plan for and size positions for it, or use defined-risk structures.
3. Record planned risk and actual loss separately so slippage past the stop is visible.

## Want it in a spreadsheet?
The Trader Toolkit ($12, Gumroad) has a trade journal that records planned risk and result in R for every trade, plus an options risk and position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance (Claude); no results claims.

Table computed by script; spot checks: 2% stop, 3% past = 2.50R; 0.5% stop, 1% past = 3.00R; $5,000 position loses $250.
