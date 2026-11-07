# Profit Factor from Win Rate and Reward-to-Risk (free table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formulas

Profit factor = gross profit / gross loss. If every loser costs 1R and every winner pays `RR` times that, with win rate `p`:

**Profit factor = (p x RR) / (1 - p)**

**Expectancy per trade = p x RR - (1 - p)** (in R, before fees)

A profit factor of 1.00 is breakeven before fees. Above 1.00 the sample made money; below 1.00 it lost.

## Table (computed by script)

| Reward : risk | Win rate | Profit factor | Expectancy |
|---|---|---|---|
| 1 : 1 | 30% | 0.43 | -0.40R |
| 1 : 1 | 40% | 0.67 | -0.20R |
| 1 : 1 | 50% | 1.00 | +0.00R |
| 1 : 1 | 60% | 1.50 | +0.20R |
| 1.5 : 1 | 30% | 0.64 | -0.25R |
| 1.5 : 1 | 40% | 1.00 | +0.00R |
| 1.5 : 1 | 50% | 1.50 | +0.25R |
| 1.5 : 1 | 60% | 2.25 | +0.50R |
| 2 : 1 | 30% | 0.86 | -0.10R |
| 2 : 1 | 40% | 1.33 | +0.20R |
| 2 : 1 | 50% | 2.00 | +0.50R |
| 2 : 1 | 60% | 3.00 | +0.80R |
| 3 : 1 | 30% | 1.29 | +0.20R |
| 3 : 1 | 40% | 2.00 | +0.60R |
| 3 : 1 | 50% | 3.00 | +1.00R |
| 3 : 1 | 60% | 4.50 | +1.40R |

Check: 2:1 at 40% gives (0.4 x 2) / 0.6 = 1.33, and expectancy 0.4 x 2 - 0.6 = +0.20R.

## Reading it honestly

- These are idealized: every win and every loss the same size. Real trades vary, so use your own journal totals.
- Fees lower profit factor. Subtract round-trip costs from gross profit and add them to gross loss before dividing.
- A high profit factor from 15 trades says little. A few lucky trades can produce it.
- Profit factor and win rate together beat either alone: 30% wins at 3:1 and 60% wins at 1:1 are different businesses.

## Want it computed from your own trades?

The **Trader Toolkit** ($12, built with AI assistance) has a journal that calculates win rate, average R, expectancy, profit factor and drawdown from your own entries, plus a position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: breakeven win rate, R-multiple and expectancy, risk-of-ruin table.
