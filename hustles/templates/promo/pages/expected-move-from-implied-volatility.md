# Expected Move Calculator: Implied Volatility to a One-Standard-Deviation Range (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

Expected move (one standard deviation) = price x IV x square root of (days to expiry / 365).

IV is the annual implied volatility quoted for the option, as a decimal. The result is the range the market is pricing as roughly a 68% chance of staying inside, if you assume a normal distribution (real markets have fatter tails).

## Move as a percent of price (computed by script)

| IV (annual) | 1 DTE | 5 DTE | 7 DTE | 14 DTE | 30 DTE | 45 DTE |
|---|---|---|---|---|---|---|
| 10% | 0.5% | 1.2% | 1.4% | 2.0% | 2.9% | 3.5% |
| 15% | 0.8% | 1.8% | 2.1% | 2.9% | 4.3% | 5.3% |
| 20% | 1.0% | 2.3% | 2.8% | 3.9% | 5.7% | 7.0% |
| 25% | 1.3% | 2.9% | 3.5% | 4.9% | 7.2% | 8.8% |
| 30% | 1.6% | 3.5% | 4.2% | 5.9% | 8.6% | 10.5% |
| 40% | 2.1% | 4.7% | 5.5% | 7.8% | 11.5% | 14.0% |
| 60% | 3.1% | 7.0% | 8.3% | 11.8% | 17.2% | 21.1% |

Check by hand: IV 20%, 1 day -> 20 x sqrt(1/365) = 20 x 0.0523 = 1.0%. IV 20%, 7 days -> 20 x sqrt(7/365) = 20 x 0.1385 = 2.8%.

## Worked example

A $500 stock with 20% IV and 7 days to expiry: 500 x 0.20 x 0.1385 = **$13.85**, so the priced one-sigma range is about $486 to $514. A short vertical spread whose short strike sits at $486 or lower is outside that range, with a rough 16% chance of being finished beyond it on that side (half of the roughly 32% outside the range).

## What it is good for
- Placing strikes relative to the market's own priced range instead of a round number.
- Sizing: the max loss of a defined-risk trade is fixed, but the chance of reaching it depends on how far the strike is from the expected move.
- Sanity-checking a stop: a stop tighter than a fraction of the day's expected move is likely to be hit by ordinary noise.

## Three cautions
- IV usually runs above the move that is later realized, and tails are fatter than normal, so use this as a ruler, not a forecast.
- Use calendar days and the IV for that expiry; weekends and event days (earnings, CPI) distort a simple 365-day scaling.
- This says nothing about whether a trade has an edge.

## Check max loss against your limit
The **Trader Toolkit** ($12, built with AI assistance) has a calculator that checks each trade's max loss against your risk limit for long options and four vertical spread types, and a journal that tracks your results: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: vertical spread max loss, credit spread break-even win rate, small-account position sizing, expected value per trade in R.
