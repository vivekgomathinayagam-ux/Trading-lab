# Kelly Criterion Table: The Math of Bet Size From Win Rate and Payoff Ratio (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

For a repeated bet that wins with probability `p` and pays `b` times the amount risked (losers lose the amount risked, so `q = 1 - p`):

**Kelly fraction f\* = p - q / b**

It is the fraction of the account that maximizes long-run growth *if* `p` and `b` are known exactly. A negative result means the bet has negative expected value, so the formula says to risk nothing.

## Full-Kelly fraction by win rate and reward-to-risk (computed by script)

Cells showing `0` mean the edge is zero or negative.

| Win rate | R 0.5 | R 1 | R 1.5 | R 2 | R 3 |
|---|---|---|---|---|---|
| 35% | 0 | 0 | 0 | 2.5% | 13.3% |
| 40% | 0 | 0 | 0 | 10.0% | 20.0% |
| 45% | 0 | 0 | 8.3% | 17.5% | 26.7% |
| 50% | 0 | 0 | 16.7% | 25.0% | 33.3% |
| 55% | 0 | 10.0% | 25.0% | 32.5% | 40.0% |
| 60% | 0 | 20.0% | 33.3% | 40.0% | 46.7% |

Check: 50% win rate, R = 2: f\* = 0.50 - 0.50 / 2 = 0.25, so 25%. 40% win rate, R = 1.5: 0.40 - 0.60 / 1.5 = 0.00, so no edge (also the breakeven win rate for R = 1.5 is 40%).

## Why real traders look at fractions of Kelly

Full Kelly assumes you know your true win rate and payoff. With a small sample you do not, and the formula is very sensitive to the estimate. Here is the same R = 2 case with a win rate that is a few points off:

| True win rate | Full Kelly | Half Kelly | Quarter Kelly |
| 30% | 0 | 0 | 0 |
| 35% | 2.5% | 1.2% | 0.6% |
| 40% | 10.0% | 5.0% | 2.5% |
| 45% | 17.5% | 8.8% | 4.4% |
| 50% | 25.0% | 12.5% | 6.2% |

If you estimate 50% and the true rate is 40%, full Kelly would have you risking 25% per trade on a bet that is worth only 10%. Full Kelly also produces large drawdowns even when the edge is real. Both are reasons many people size far below it.

## A hard ceiling is a separate rule

Kelly is about growth. A per-trade loss cap is about survival. A fixed cap such as 2% or 5% of the account on max loss per trade applies *on top* of any Kelly number: use the smaller one. For a defined-risk options trade, the risk is the max loss (debit paid, or spread width minus credit, times 100, times contracts).

Example, $1,000 account, 5% cap = $50 max loss. A $2.00-wide vertical debit spread costing $0.80 has a max loss of $80 per contract, which is over the cap, so zero contracts fit. This is the check the calculator below automates.

## Check your own numbers

The **Trader Toolkit** ($12, built with AI assistance) has a journal that computes your actual win rate, average win and loss, R multiples and expectancy from your own logged trades, and a position-size calculator that tests a trade's max loss against your risk limit: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: breakeven win rate by reward-to-risk, profit factor table, risk-of-ruin table, R-multiple and expectancy explained.
