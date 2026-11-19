# Risk-Reward Ratio for a Long Option: Stop % and Target % Table (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

When you buy a call or put, you can express the plan as a percent move in the option's premium: a stop (how much of the premium you will give up) and a target (how much gain you will take). The risk-reward ratio is target % divided by stop %.

## The formula

`risk-reward = target gain % / stop loss %`  (both measured on the option premium)

## Table: risk-reward ratio by stop and target

| Target gain \ Stop loss | 20% | 25% | 30% | 40% | 50% |
|---|---|---|---|---|---|
| 25% | 1.25 | 1.00 | 0.83 | 0.62 | 0.50 |
| 50% | 2.50 | 2.00 | 1.67 | 1.25 | 1.00 |
| 75% | 3.75 | 3.00 | 2.50 | 1.88 | 1.50 |
| 100% | 5.00 | 4.00 | 3.33 | 2.50 | 2.00 |
| 150% | 7.50 | 6.00 | 5.00 | 3.75 | 3.00 |
| 200% | 10.00 | 8.00 | 6.67 | 5.00 | 4.00 |

Read across: a 25% stop with a 75% target is 3.00 to 1.

## Worked example (one contract)

Premium $2.00 per share ($200 per contract). Stop at 25%: exit at $1.50, risk = $0.50 x 100 = **$50**. Target at 75%: exit at $3.50, gain = $1.50 x 100 = **$150**. Ratio = 150 / 50 = **3.00**.

## What the ratio does not tell you

A high ratio is only half of the picture. The ratio sets the win rate you need just to break even: `breakeven win rate = 1 / (1 + ratio)`. At 3.00 that is 25% (before commissions and the bid-ask spread). At 1.00 it is 50%. Whether your setups actually win that often is something only your own journal can show.

Two practical cautions: option premiums can gap through a stop, so real losses can exceed the planned stop; and wide bid-ask spreads on cheap options mean your real entry is already below the mid price, which lowers your real ratio.

## Want it in a spreadsheet?

The Trader Toolkit ($12, Gumroad) has an options risk and position-size calculator (long options and vertical spreads, with a risk-limit check) plus a trade journal with R-multiple stats, drawdown and streaks: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance; no results claims.
