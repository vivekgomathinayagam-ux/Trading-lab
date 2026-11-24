# Long Option: How Far Must the Underlying Move to Recover the Premium? (free table)

When you buy a call or put, the option has to gain back what you paid. A rough way to see how far the underlying must move: divide the premium by the option's delta. Delta is the approximate change in the option price per $1 move in the underlying. This is an approximation only: delta changes as price moves, and time decay and implied-volatility changes also move the price. Arithmetic only: not advice, not a signal, no prediction of results. Options involve risk of loss.

## The formula
Approx. underlying move needed = premium per share / delta

Example: a $1.00 option with delta 0.50 needs roughly a $2.00 move in the underlying in your favor, all else equal, to be worth $2.00 (a gain equal to the premium paid).

## Table: approximate $ move in the underlying to gain back the premium paid
| Premium per share | Delta 0.20 | Delta 0.30 | Delta 0.50 | Delta 0.70 |
|---|---|---|---|---|
| $0.50 ($50 per contract) | $2.50 | $1.67 | $1.00 | $0.71 |
| $1.00 ($100 per contract) | $5.00 | $3.33 | $2.00 | $1.43 |
| $2.00 ($200 per contract) | $10.00 | $6.67 | $4.00 | $2.86 |
| $3.00 ($300 per contract) | $15.00 | $10.00 | $6.00 | $4.29 |
| $5.00 ($500 per contract) | $25.00 | $16.67 | $10.00 | $7.14 |

Read it like this: a $0.50 option with delta 0.20 needs about a $2.50 move just to gain $0.50, while the same premium on a delta 0.70 option needs about $0.71. Lower-delta options are cheaper but need bigger moves.

## Worked example in dollars
You pay $2.00 per share ($200 per contract) for a call with delta 0.30. Approx. move needed to gain back $2.00: $2.00 / 0.30 = $6.67. If the stock is at $100, that is about 6.7% in your favor, and it must happen before time decay eats the premium. Your maximum loss is the $200 paid.

## How to use it
1. Before entry, divide the premium by the delta and ask whether that move is realistic inside your holding time.
2. Compare with the expected-move page (implied volatility) to see what the market already prices.
3. Size by the premium you can lose, not by the move you hope for: see the small-account sizing page.

## Want it in a spreadsheet?
The Trader Toolkit ($12, Gumroad) has a trade journal with R-multiple stats plus an options risk and position-size calculator for long options and vertical spreads: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance (Claude); no results claims.

Table computed by script; spot checks: $1.00 / 0.50 = $2.00; $3.00 / 0.30 = $10.00; $0.50 / 0.20 = $2.50.
