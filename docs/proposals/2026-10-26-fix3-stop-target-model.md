# Proposal: realistic stop and target fills (Fix 3) — FOR REVIEW, NOT IMPLEMENTED

_Vivek, 2026-10-26: don't fill every stop or target at its exact price just to match the backtest. That would be too optimistic. Model stop and target execution realistically, including gaps, slippage, and whether a target order could actually fill. Explain before changing anything._

## Today's behavior (unchanged)
| | Backtest (lab) | Paper (bot) |
|---|---|---|
| Stop | exact stop price, or the bar's open if it gapped through | live Yahoo price ~43 s after the 1-min bar closes, minus 0.02% / 0.05% slippage |
| Target | exact target price as soon as the bar's high touches it | same as stop: live price ~43 s after the bar |
| Same bar touches both | stop counts | stop counts |

Problems:
- The backtest is optimistic in two ways. Stops fill exactly at the stop, with no extra slip in a fast drop. Targets fill on a mere touch, even though a real limit order at that price may not fill: other orders were ahead of it in the queue.
- Paper is arbitrary. The ~43-second delay can help or hurt, and the backtest can't reproduce it.
- So the two systems aren't comparable.

## Proposed model (same code for backtest and paper, in `strategies/daytrade/core.py`)
1. **Stop = a resting stop-market order.**
   - Triggers when a bar's low ≤ stop.
   - Fill = min(bar open, stop) × (1 − stop slippage).
   - Stop slippage is larger than normal slippage, because stops fire into moving prices.
   - Proposed: **0.05% for SPY/QQQ, 0.15% for 3x ETFs** [assumption, configurable].
   - A gap through the stop fills at the open, minus slippage.
2. **Target = a resting limit sell at the target.**
   - Fills only if price trades **through** the limit: bar high ≥ target + buffer, buffer = max($0.01, 0.01% of price) [assumption, configurable].
   - A touch without going through = **not filled**; the position stays open.
   - A gap above the target fills at the bar's open (a resting limit gets the better price).
   - No slippage on a limit fill (the price is the limit or better).
3. **Same bar hits both:** the stop counts (unchanged, conservative).
4. **Paper uses the same rule.** It fills at the modeled price, not at the live price ~43 s later.
   - The live price stays in `daytrade_fills.csv` as a reality check, already logged as `raw_px` next to `rule_px`.
   - If, over the coming weeks, modeled stop fills come out consistently better than live prices at detection, the stop slippage gets raised. It never gets lowered to flatter results.
5. **EOD (Fix 4) stays separate.** We first collect the 15:55-open vs ~15:56:43-live comparison, then pick one rule for both systems.

## Why this is more realistic, not more optimistic
- Stops: worse than today's backtest (extra slippage). Gaps are kept.
- Targets: harder to fill than today's backtest (must trade through). Gaps are rewarded only the way a real resting limit would be.
- Both systems use one rule, so "paper close to backtest" becomes a meaningful gate again.

## Limits
- With 1-minute bars we can't see the path inside a minute or the real order queue. This is a model, not a replay.
- No bid/ask data (Yahoo has none), so slippage is assumed. The Skylit cross-check and live `raw_px` measure how wrong the assumption is.
- It's a change to pre-registered rules, so it counts as a new variant. The lab reruns all 6 rules under both the old and new fill models and reports both.

## Files that would change (after your yes)
- `strategies/daytrade/core.py`: `Desk.exit_check` (stop/target fill prices, target buffer), new config params.
- `engine/daytrade_runner.py`: stop/target exits fill at the rule price instead of the live price.
- `lab/floor/engine.py` / `lab/floor/run.py`: rerun the backtest with both models.
- Tests for gaps, touch-not-filled targets, same-bar ties, and the slippage math.

Decision needed: approve the model, change the slippage or buffer numbers, or keep today's behavior.
