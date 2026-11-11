# Expected Value Per Trade in R: Win Rate and Reward-to-Risk Table (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

Measure every trade in R, where 1R is the amount you risk (the max loss you accepted at entry). If your average winner is `R:R` times your risk and your average loser is 1R:

**Expected value per trade (in R) = win rate x R:R - (1 - win rate)**

Positive means the average trade added to the account over a large sample; negative means it took away. Before commissions and fees, and only as good as the win rate and R:R you measured from real trades.

## Expected value per trade in R (computed by script)

| Win rate | R:R 0.5 | R:R 1 | R:R 1.5 | R:R 2 | R:R 3 |
|---|---|---|---|---|---|
| 30% | -0.55R | -0.40R | -0.25R | -0.10R | +0.20R |
| 40% | -0.40R | -0.20R | +0.00R | +0.20R | +0.60R |
| 50% | -0.25R | +0.00R | +0.25R | +0.50R | +1.00R |
| 60% | -0.10R | +0.20R | +0.50R | +0.80R | +1.40R |
| 70% | +0.05R | +0.40R | +0.75R | +1.10R | +1.80R |

Check by hand: 50% win rate, R:R 1.5 -> 0.50 x 1.5 - 0.50 = +0.25R. 40% at R:R 1.5 -> 0.60 - 0.60 = 0.00R (break-even).

## Worked example in dollars

Win rate 45%, R:R 2: EV = 0.45 x 2 - 0.55 = +0.35R. With 1R = $50, that is +17.50 dollars per trade on average, before fees. Ten trades is far too few to trust: a 45% win rate can easily show up as 2 wins in 10 by chance.

## Three cautions
- The inputs come from your own trade history. Too few trades and the table is guesswork; 30 is a bare minimum and 100 or more is better.
- Fees count. On a small account, commissions on a $50 risk can be a visible slice of 1R. Subtract them.
- Win rate and R:R move together. Tightening a target usually raises win rate and lowers R:R. Use the same trades to measure both.

## Get the inputs from your own trades
The **Trader Toolkit** ($12, built with AI assistance) has a journal that computes your win rate, average R, expectancy, profit factor and drawdown from your own trade log, and a calculator that checks a trade's max loss against your risk limit: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: breakeven win rate by reward-to-risk, profit factor table, R-multiple expectancy explained, Kelly fraction table.
