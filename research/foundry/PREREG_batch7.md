# Foundry batch 7: pre-registration (Researcher, Sat 2026-11-21 review run)

Written and committed BEFORE any of these numbers were computed. Research only; nothing here trades.

## Data
- **M** = Alpaca 1-min archive, SPY QQQ TQQQ UPRO SQQQ SPXU, 2022-01-03 to 2026-11-18 (`data:backtests/data/alpaca1m/`, first use). Regular hours only.
- **Development** = 2022-2025; **holdout** = 2026 (opened once, after the development ranking is committed). Halves of development = 2022-2023 and 2024-2025.
- Replay = the paper desks' own code (`strategies/daytrade/core.py`: `Features`, rule `signal()`, `Desk` order of operations): signal at a bar's close, fill at the next bar's open + slippage (`SLIP`: 0.02% SPY/QQQ, 0.05% 3x ETFs per side), +5% target, −2.5% stop, flat at 15:55, one entry per day per desk, symbol priority on ties, first 3 sessions warm-up. Sized as the $1,000 desk without compounding (qty = floor(1000 / entry price)); statistic = P&L as % of $1,000 per trade. 2x costs = slippage x2.
- Implementation: every rule signal is extracted once per symbol by the core `Features` class; each signal's trade outcome is computed with the `Desk` exit rules; a variant's trades are its first passing signal of each day. Test: this equals `lab.floor.engine.simulate` on the base rule (exact match required on a sample before any variant is read).
- Random control: per session one random entry minute 09:35-15:29 on a random symbol of the same side group, same exits; the rule must beat the 95th percentile of the mean of n random trades (n = rule's trade count, 500 draws).

## Volspike MA grid (registered 2026-11-18, `PREREG_volspike_grid.md`; run now, unchanged)
Implementation details fixed here because the 11-18 text left them open:
- MA on timeframe TF ∈ {1, 5, 15} min: clock buckets from 09:30; the value used at a signal is that of the last bucket closed at or before the signal bar's close (bucket close = its last bar's close), series continuous across sessions (no reset).
- Slope "up" = MA now > MA 3 buckets earlier. Inverse ETFs in the underlying view are mirrored (SQQQ: QQQ close < MA, slope down, fast < slow). For SPY and QQQ the underlying view equals the own view.
- Random-filter null: 1,190 random filters, each keeping each signal with the real filter's signal keep rate; statistic = development expectancy minus the base's.
- Bonferroni: one-sided Welch t of the top filter's development trades vs the base's development trades, p x 1,190.

## H25: the volume gate on ORB and EMA (coach, BOARD 2026-11-19 / 11-20)
ORB (`ORB`) and EMA 9/21 (`EMACross`) with the volume gate at 3x (paper), 1.5x and none (lab comparators); long side = SPY/QQQ/TQQQ/UPRO signals only, short side = SQQQ/SPXU signals only (each side run as its own desk, so 6 cells x 2 sides). Question: does the 3x gate help? Prediction if the gate is useful: 3x > none in expectancy on development in both halves and both sides, and on the 2026 holdout. If none ≥ 3x on development in both halves for both rules, the gate is refuted as an edge source (it only cuts trade count). Any cell that passes the full bar (below) is a desk candidate.

## H26: one slot per side (coach, BOARD 2026-11-20 item 1)
ORB plain, EMA plain and volspike as the paper desk (one entry per day across all 6 ETFs) vs a desk with one long slot (SPY/QQQ/TQQQ/UPRO) and one short slot (SQQQ/SPXU) per day, each slot entered at most once. Statistic: per-trade expectancy and total P&L per session. Prediction if the coach is right: the two-slot version adds trades with expectancy ≥ the one-slot version's, on development, both halves and the holdout. It is a sizing/slot question: it ships only with a rule that has edge.

## Pass bar (any rule cell)
Development: mean > 0 with bootstrap (day-block) 95% CI lower bound > 0, > 0 in both development halves, > 0 at 2x costs, above the random-control p95, ≥ 100 trades. Holdout 2026: mean > 0 and ≥ 20 trades. A cell that passes goes to paper as a new desk key.

## Newsie shadow (standing)
As batch 6, on all Newsie days to date (Nov 18-20): sit_out / caution / bias per paper desk. Shadow only until 20+ Newsie days.

## Variants counted
Volspike grid 1,190 + base; H25 3 gates x 2 rules x 2 sides = 12; H26 3 rules x 2 slot designs = 6 (3 new). Newsie 3 flags x 4 desks (counted in batch 6, not again).
