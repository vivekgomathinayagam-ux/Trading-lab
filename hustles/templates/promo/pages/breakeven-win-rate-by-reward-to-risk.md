# Breakeven Win Rate by Reward-to-Risk Ratio (free table, fees included)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

If every trade risks 1R and wins pay `RR` times that, expectancy per trade = `p x RR - (1 - p) - fee`, where `p` is win rate and `fee` is round-trip costs measured in R. Setting it to zero gives the breakeven win rate:

**p = (1 + fee) / (1 + RR)**

## Table (computed by script)

| Reward : risk | No fees | Fees = 0.05R per trade | Fees = 0.10R per trade |
|---|---|---|---|
| 0.5 : 1 | 66.7% | 70.0% | 73.3% |
| 0.75 : 1 | 57.1% | 60.0% | 62.9% |
| 1 : 1 | 50.0% | 52.5% | 55.0% |
| 1.25 : 1 | 44.4% | 46.7% | 48.9% |
| 1.5 : 1 | 40.0% | 42.0% | 44.0% |
| 2 : 1 | 33.3% | 35.0% | 36.7% |
| 2.5 : 1 | 28.6% | 30.0% | 31.4% |
| 3 : 1 | 25.0% | 26.2% | 27.5% |
| 4 : 1 | 20.0% | 21.0% | 22.0% |

Check: at 2:1 and a 33.3% win rate, expectancy = 0.333 x 2 - 0.667 = 0. A 40% win rate at 1.5:1 with 0.05R fees gives 0.4 x 1.5 - 0.6 - 0.05 = -0.05R, a small loss even though it looks "breakeven" before fees.

## How to use it

- Fees matter more on small trades: if you risk $80 and pay $4 round trip, that is 0.05R.
- Your measured win rate needs dozens of trades to mean anything; ten trades can swing 20 points by luck.
- Win rate alone says nothing. Compare it with the breakeven for the reward-to-risk you actually got.

## Want it computed for you?

The **Trader Toolkit** ($12, built with AI assistance) has a journal that calculates win rate, average R, expectancy, profit factor and drawdown from your own trades, plus a position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: R-multiple and expectancy, risk-of-ruin table, small-account position sizing.
