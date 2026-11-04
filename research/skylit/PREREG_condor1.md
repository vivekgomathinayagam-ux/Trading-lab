# Skylit condor study 1: 1-day SPY iron condor at ±1 priced sigma (pre-registered)

Written 2026-11-04 16:20 PT by the Researcher, **before any option price was pulled**. Queue item 1 since Oct 31. Lead: LESSONS 5 (realized next-day move ≈ 0.7x priced).

## Trade
- Entry: SPY at the 15:45 ET 1-min bar close (archive A), day D. Sigma = Tempest `em_1d_pct` at D's close (priced for D+1).
- Short call strike = ceil(S × (1 + σ)), short put strike = floor(S × (1 − σ)); long wings $5 further out. Expiry = next trading day D+1 (SPY dailies).
- Leg prices: close of each contract's 15:45 ET 5-min bar from Skylit `contract_chart` (trade prices; Skylit has no historical bid/ask). Cost model: every leg filled $0.02 worse than that print on entry (sell lower, buy higher); 2x stress $0.04. Commission $0.65 per contract per leg, 4 legs in. A leg with no trade in the 15:30-15:55 window → the day is dropped and counted.
- Exit: held to D+1 close (last 1-min close of the archive). Value = intrinsic; any leg in the money is closed at intrinsic with another $0.02 per ITM leg and $0.65 commission.
- Max loss per condor = $500 − credit. Report P&L per condor in $ and as % of max loss.

## Sample
Every D from Oct 5 to Nov 2, 2026 (contract_chart's 30-day window), one condor a day, ≈ 21 trades. Both halves reported. Days with an event (none in Tempest flags expected) reported separately.

## Pass bar (promising → options paper path proposal)
1. Mean P&L > 0 after costs AND after 2x costs.
2. Positive in both halves.
3. Breach rate (short strike crossed at D+1 close) ≤ 25%.
4. Worst single loss stated; the study cannot prove tail safety with ~21 trades, so a pass is "promising", never "works".
Even on a pass, paper needs an options order path in `engine/` → one unmerged PR + one City Hall item for Vivek. Wrong if mean ≤ 0 after 1x costs.

## Variants
1 (no grid). Running total 155 → 156. Credits: about 21 × 4 × 3 = 252 plus 1 for Tempest.
