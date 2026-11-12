# Losing Streak Probability Table: How Many Losses in a Row Are Normal? (free)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## Chance that the next N trades all lose

If each trade is independent and you lose a fraction `L` of the time, the chance of N losses in a row starting now is **L to the power N**.

| Win rate | 3 losses | 5 losses | 7 losses | 10 losses |
|---|---|---|---|---|
| 30% | 34.3% | 16.8% | 8.2% | 2.8% |
| 40% | 21.6% | 7.8% | 2.8% | 0.6% |
| 50% | 12.5% | 3.1% | 0.8% | 0.1% |
| 60% | 6.4% | 1.0% | 0.2% | 0.0% |
| 70% | 2.7% | 0.2% | 0.0% | 0.0% |

Check by hand: 50% win rate, 5 in a row -> 0.5 x 0.5 x 0.5 x 0.5 x 0.5 = 3.1%. 60% win rate, 3 in a row -> 0.4 x 0.4 x 0.4 = 6.4%.

## Chance of seeing a streak at least once in 100 trades (computed by script)

The table above is for one specific starting point. Over a whole stretch of trading, a streak showing up somewhere is much more likely.

| Win rate | 5+ losses in a row | 7+ losses in a row | 10+ losses in a row |
|---|---|---|---|
| 30% | 100% | 95% | 58% |
| 40% | 98% | 69% | 20% |
| 50% | 81% | 32% | 4% |
| 60% | 46% | 9% | 1% |
| 70% | 15% | 1% | 0% |

Computed exactly by dynamic programming over 100 independent trades.

## What it means for position size

A streak that looks "impossible" is often ordinary. If you lose 5 in a row at 1R each and risk 5% per trade, the account is down about 22.6% (1 - 0.95^5), and it then needs about a 29% gain to recover. Risking 1% per trade, the same streak costs about 4.9%. The streak is the same; the size decides whether it is a bad week or a blown account. Pick the size by asking "what is the longest streak I should be able to sit through?", not "what do I expect to win?".

## Three cautions
- Real trades are not perfectly independent (market regimes cluster), so real streaks can run longer than this table.
- The win rate must come from your own logged trades. With fewer than 30 trades it is mostly noise.
- This says nothing about whether a strategy works. It only shows what bad luck alone looks like.

## Track your own streaks
The **Trader Toolkit** ($12, built with AI assistance) has a journal that shows your win rate, longest winning and losing streaks, drawdown and expectancy from your own trade log, and a calculator that checks each trade's max loss against your risk limit: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: risk of ruin table, drawdown recovery (gain needed), expected value per trade in R, small-account position sizing.
