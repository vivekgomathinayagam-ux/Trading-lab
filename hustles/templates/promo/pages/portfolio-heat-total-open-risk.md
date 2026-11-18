# Portfolio Heat: Total Open Risk Across Several Options Positions (free table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

"Portfolio heat" is the total amount you would lose if every open position hit its planned max loss at the same time. A 1% risk rule per trade is not a 1% rule for the account once three trades are open.

## The formula

`heat % = sum of (planned max loss of each position x contracts) / account size x 100`

If every position risks the same percent, heat = risk per trade x number of open positions.

## Table: heat when every position risks the same percent

| Open positions | 0.5% each | 1% each | 2% each | 3% each | 5% each |
|---|---|---|---|---|---|
| 1 | 0.5% | 1% | 2% | 3% | 5% |
| 2 | 1% | 2% | 4% | 6% | 10% |
| 3 | 1.5% | 3% | 6% | 9% | 15% |
| 4 | 2% | 4% | 8% | 12% | 20% |
| 5 | 2.5% | 5% | 10% | 15% | 25% |
| 6 | 3% | 6% | 12% | 18% | 30% |

Read across: six positions at 2% each puts 12% of the account at risk at once, even though no single trade breaks a 2% rule.

## Worked example ($10,000 account)

| Position | Contracts | Max loss per contract | Risk | % of account |
|---|---|---|---|---|
| SPY 570C | 1 | $150 | $150 | 1.50% |
| QQQ put debit spread | 1 | $200 | $200 | 2.00% |
| SPY call credit spread | 2 | $180 | $360 | 3.60% |
| **Total open risk** | | | **$710** | **7.10%** |

Check: 150 + 200 + 2 x 180 = $710, and 710 / 10,000 = 7.10%.

## Correlation caveat

SPY, QQQ and SPX options tend to move together. In a sharp market move they can all lose at once, so many traders count same-direction index positions as one position when deciding how much total heat to allow. The table above is the worst case where all of them hit their stops together.

## Setting a heat cap

Pick a cap in advance (for example 3%, 5% or 6% of the account, your choice) and write it next to your per-trade limit. Before opening a new position, add its risk to the open heat. If the total passes your cap, skip the trade or size it smaller. This page only does the sum; the cap is yours to choose.

## Want it in a spreadsheet?

The Trader Toolkit ($12, Gumroad) has an options risk and position-size calculator (long options and vertical spreads, with a risk-limit check) plus a trade journal with R-multiple stats, drawdown and streaks: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance; no results claims.
