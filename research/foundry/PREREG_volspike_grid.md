# Volspike trend-filter grid: pre-registration (Researcher, 2026-11-18)

Asked for by Vivek (BOARD 2026-11-17, item 2). Registered before the data exists; nothing has been computed.

## Data
- Alpaca 1-minute bars, SPY QQQ TQQQ UPRO SQQQ SPXU, 2022-01-03 to the latest session (`data:backtests/data/alpaca1m/`, built by the `alpaca-history` workflow from 2026-11-18).
- **Development** = 2022-2025. **Holdout** = 2026 sessions, opened once, after the development ranking is frozen in a commit.

## Base rule (unchanged)
The paper `volspike` rule (`strategies/daytrade/core.py`, class `VolSpike`), replayed bar by bar through `lab/floor` on each ETF exactly as the bot runs it: spike bar closes up, above VWAP and the prior 15-bar high; sized as the $1,000 desk; +5% target, −2.5% stop, flat 15:55. Costs: the floor-lab cost model and 2x.

## Grid (filters applied at the signal bar's close, using bars up to that close only)
- MA type {EMA, SMA} x length {5, 8, 9, 10, 13, 20, 21, 34, 50, 100, 200} x timeframe {1, 5, 15 min} x test {price above MA, MA slope up over its last 3 bars} = 264 single filters.
- Fast-over-slow pairs (same type and timeframe), fast < slow from the length list: 55 pairs x 2 types x 3 timeframes = 330.
- Total 594 filters + the unfiltered base = 595 variants. Short exposure is already in the rule (it trades SQQQ/SPXU spikes); every filter is applied to the traded ETF's own bars and, as a second view, to the underlying index (SPY for UPRO/SPXU, QQQ for TQQQ/SQQQ, mirrored for inverse ETFs). That doubles the count: **1,190 variants**.

## Selection and pass bar
- Rank on development by expectancy per trade after costs, minimum 100 development trades.
- Multiple testing: report how many of the 1,190 beat the base on development by more than the 95th percentile of the same statistic for 1,190 random filters (each random filter keeps each base trade with probability equal to the real filter's keep rate). Also the Bonferroni-adjusted p for the top filter.
- The top 3 by development expectancy go to the holdout. A filter becomes `volspike_v2` on paper only if on the 2026 holdout it (a) beats the base volspike's expectancy, (b) has a positive expectancy with a 95% CI lower bound above the base's mean, (c) is positive in both halves of the holdout and at 2x costs, and (d) keeps at least 20 holdout trades.
- If none passes: volspike stays as is and the grid is logged as a refuted family.
