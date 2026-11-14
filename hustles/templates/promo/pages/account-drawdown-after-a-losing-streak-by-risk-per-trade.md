# Account Drawdown After a Losing Streak, by Risk Per Trade (free table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

If you risk a fixed percent r of your *current* account on each trade and lose N trades in a row, the account is worth (1 - r)^N of where it started. Drawdown = 1 - (1 - r)^N.

## Drawdown after N straight full-risk losses (computed by script)

| Risk per trade | 3 losses | 5 losses | 8 losses | 10 losses | 15 losses | 20 losses |
|---|---|---|---|---|---|---|
| 0.5% | -1.5% | -2.5% | -3.9% | -4.9% | -7.2% | -9.5% |
| 1% | -3.0% | -4.9% | -7.7% | -9.6% | -14.0% | -18.2% |
| 2% | -5.9% | -9.6% | -14.9% | -18.3% | -26.1% | -33.2% |
| 3% | -8.7% | -14.1% | -21.6% | -26.3% | -36.7% | -45.6% |
| 5% | -14.3% | -22.6% | -33.7% | -40.1% | -53.7% | -64.2% |
| 10% | -27.1% | -41.0% | -57.0% | -65.1% | -79.4% | -87.8% |

Check by hand: 2% risk, 10 losses -> 0.98^10 = 0.817, so -18.3%. 5% risk, 5 losses -> 0.95^5 = 0.774, so -22.6%. 10% risk, 8 losses -> 0.9^8 = 0.430, so -57.0%.

## How to use it
- Pick the drawdown you could tolerate (for example a funded-account limit or a personal stop) and the losing streak you want to survive, then read off the largest risk per trade that stays inside it.
- Compare with the losing-streak probability table: a streak of 8 is rare at a 50% win rate but not impossible over hundreds of trades.
- Losses compound on a shrinking balance, so the drawdown is a little smaller than N x r.

## Cautions
- Assumes every loss costs the full planned risk. Gaps, slippage and fees can make a loss larger.
- Says nothing about whether a strategy has an edge.

## Check each trade's max loss against your limit
The **Trader Toolkit** ($12, built with AI assistance) has a calculator that checks each trade's max loss against your risk limit for long options and four vertical spread types, and a journal that tracks your results: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: losing-streak probability table, drawdown recovery gain needed, risk of ruin table, small-account position sizing.
