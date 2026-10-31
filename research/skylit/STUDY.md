# Skylit edge study: log (the Researcher)

## Pilot 1, registered 2026-10-28 before computing any result
Data: Heatseeker historical boards at 10:00 ET (asOf <= 09:59:59 ET), SPY and QQQ, 40 strikes around spot,
nearest 2 expirations (0DTE + next), 62 sessions 2026-08-03..2026-10-28 (raw cache on branch `data`: `research/skylit/raw/heat_1000et_part*.jsonl`).
Outcomes: Skylit daily board spot close (`heat_stats_daily`, cached on branch `data`: `research/skylit/raw/stats_daily_close.json`, cross-checked against Yahoo closes within 0.04%).
Questions (fixed now; each is one variant):
1. **King pull:** does the close move toward the king strike? Measure sign(close - spot10) vs sign(king - spot10) hit rate,
   and the share of days the close ends nearer the king than spot10 was. Null: 50%.
2. **Gamma regime vs movement:** net gamma = sum of the 40 strike values. Is |close - spot10| / spot10 smaller on net-positive
   days than net-negative days? (Positive dealer gamma = dealers dampen moves.)
3. **King sign:** does a positive-value king pin harder (smaller |close - king|/spot) than a negative-value king?
Method: hit rates with a binomial 95% interval; mean differences with a bootstrap 95% CI. 62 days x 2 symbols, and SPY and QQQ
are highly correlated, so the effective sample is closer to 62. Pilot only: a finding here gets a pre-registered setup and a
forward test, never a trade directly.

### Pilot 1 result (2026-10-28)
| Question | SPY | QQQ | Both |
|---|---|---|---|
| Close moves toward king (null 50%) | 49% [36, 62], n=59 | 43% [30, 56], n=56 | 46% [37, 55] |
| Mean abs move 10:00->close, net gamma >0 minus <=0 | −0.06 pts [−0.19, +0.06] | +0.07 [−0.12, +0.27] | +0.01 [−0.11, +0.14] |
| Close-to-king distance, positive king minus negative king | +0.05 [−0.15, +0.25] | +0.28 [0.00, +0.59] | +0.17 [−0.01, +0.37] |
- No king pull, no dampening on positive-gamma days, and positive kings did not pin harder (if anything the reverse).
- The "close nearer the king than at 10:00" share (34%) is not a test: the king usually sits within 0.1-0.3% of spot,
  so almost any move ends farther away. Reported only for completeness.
- Reading: at this horizon (10:00 to close) and with this definition (2 nearest expirations, 40 strikes), the board has
  no usable directional or range information. That does not rule out shorter horizons or 0DTE-only boards (pilot 2).
- Credits: 62 calls of 5 credits (each holds SPY and QQQ) + 4 daily-stats calls + 3 checks = 341.

## Pilot 2, registered 2026-10-31 (Saturday review run) before pulling or computing anything
Horizon: intraday, next 60 and 90 minutes. Data: Heatseeker historical boards, **0DTE only** (`max_expirations=1`), 60 strikes
around spot, SPY and QQQ, at **10:00 and 12:30 ET** (asOf <= the decision minute), every session in the 1-minute archive
(2026-09-28 .. 2026-10-30, about 25 sessions). Outcomes from the 1-minute archive (`backtests/data/etf1m/`, bars that START at or
after the decision minute; the decision uses nothing later). Raw pulls cached on branch `data` under `research/skylit/raw/heat0dte_*.jsonl`.
Definitions (fixed now):
- spot = the board's spot; magnet = strike with the largest positive gamma within ±1% of spot; accelerant = strike with the most
  negative gamma within ±1%; net0 = sum of gamma over the 60 strikes.
- Q2.1 **Magnet pull:** over the next 60 min, does price move toward the magnet (sign of close(t+60) - spot vs sign(magnet - spot))?
  Only when |magnet - spot| > 0.05%. Null 50%. Binomial 95% CI.
- Q2.2 **Gamma regime vs range:** next-60-min range (high-low)/spot, net0 > 0 minus net0 <= 0. Bootstrap 95% CI (day blocks).
- Q2.3 **Accelerant proximity:** next-60-min range when spot is within 0.25% of the accelerant minus when it is not. Bootstrap CI.
- Q2.4 Same three at 90 minutes (reported, not separately counted as new ideas: 3 more variants).
Tempest (daily, ~2 years, SPY and QQQ, `tempest_history`; cached as `research/skylit/raw/tempest_hist_*.json`):
- Q2.5 **Priced vs realized 1-day move:** share of next sessions whose |close-to-close| exceeds the prior close's `em_1d_pct`
  (normal-model null ≈ 31.7%), and mean |move|/em_1d. Below 1 = the market overprices next-day moves (premium for defined-risk sellers).
  Split chronologically into halves; a finding must hold in both.
- Q2.6 **Term slope:** breach rate (Q2.5) in the top vs bottom third of `term slope` (whatever sign convention Tempest uses, stated in
  the result). Bootstrap CI on the difference; must hold in both halves.
Variants: 6 heat questions x 2 horizons... counted as 6 (Q2.1-2.3 at 60 and 90) + 2 Tempest = 8. Pilot only: anything that holds
gets a pre-registered setup and forward paper, never a trade directly. Expected credits: ~25 sessions x 2 times x 5 = 250, Tempest ~150.
