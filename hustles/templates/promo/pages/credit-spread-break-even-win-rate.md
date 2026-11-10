# Credit Spread Break-Even Win Rate: How Often a Short Vertical Must Win (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

A short vertical (bull put or bear call credit spread) collects a credit `C` per share and has a width `W` between strikes. Per contract (100 shares):

- Max profit = C x 100
- Max loss = (W - C) x 100
- **Break-even win rate = max loss / (max profit + max loss) = (W - C) / W**

This counts only full wins (keep the whole credit) and full losses (lose the whole max loss). Real trades often close early, so treat it as a rough yardstick, before commissions and fees.

## Break-even win rate by credit as a share of width (computed by script)

| Credit / width | Break-even win rate | Reward-to-risk |
|---|---|---|
| 10% | 90.0% | 0.11 |
| 15% | 85.0% | 0.18 |
| 20% | 80.0% | 0.25 |
| 25% | 75.0% | 0.33 |
| 30% | 70.0% | 0.43 |
| 33% | 67.0% | 0.49 |
| 40% | 60.0% | 0.67 |
| 50% | 50.0% | 1.00 |

Check: $1 wide, $0.30 credit: max profit $30, max loss $70, break-even = 70 / 100 = 70%. A trade that wins 7 of 10 full-size breaks even before costs; anything less loses money on average.

## Dollar examples per contract

| Width | Credit | Max profit | Max loss | Break-even win rate |
|---|---|---|---|---|
| $1 | $0.20 | $20 | $80 | 80% |
| $1 | $0.30 | $30 | $70 | 70% |
| $1 | $0.50 | $50 | $50 | 50% |
| $2 | $0.20 | $20 | $180 | 90% |
| $2 | $0.30 | $30 | $170 | 85% |
| $2 | $0.50 | $50 | $150 | 75% |
| $5 | $0.20 | $20 | $480 | 96% |
| $5 | $0.30 | $30 | $470 | 94% |
| $5 | $0.50 | $50 | $450 | 90% |

## Two cautions
- The break-even win rate is high for small credits. A 20%-of-width credit needs an 80% win rate just to break even, and the occasional full loss erases several wins.
- Fees matter more on small credits. Commissions on four legs (open and close) can take a visible share of a $20 credit. Recompute with your broker's actual fees.

## Check it against your own account limit
Max loss is also what a per-trade risk cap is tested against. With a $1,000 account and a 5% cap ($50), a $1-wide spread with a $0.30 credit has a max loss of $70, which is over the cap: zero contracts fit. A $1-wide spread with a $0.55 credit has a max loss of $45, which fits one contract.

The **Trader Toolkit** ($12, built with AI assistance) has a position-size calculator that tests a vertical spread's max loss against your risk limit, and a journal that computes your actual win rate and expectancy from your own trades: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: vertical spread max loss calculator, breakeven win rate by reward-to-risk, profit factor table, small-account options position sizing.
