# Skylit edge study: log (the Researcher)

## Pilot 1, registered 2026-10-28 before computing any result
Data: Heatseeker historical boards at 10:00 ET (asOf <= 09:59:59 ET), SPY and QQQ, 40 strikes around spot,
nearest 2 expirations (0DTE + next), 62 sessions 2026-08-03..2026-10-28 (raw: `research/skylit/raw/heat_1000et_part*.jsonl`).
Outcomes: Skylit daily board spot close (`heat_stats_daily`, raw cached in `research/skylit/raw/stats_daily.json`).
Questions (fixed now; each is one variant):
1. **King pull:** does the close move toward the king strike? Measure sign(close - spot10) vs sign(king - spot10) hit rate,
   and the share of days the close ends nearer the king than spot10 was. Null: 50%.
2. **Gamma regime vs movement:** net gamma = sum of the 40 strike values. Is |close - spot10| / spot10 smaller on net-positive
   days than net-negative days? (Positive dealer gamma = dealers dampen moves.)
3. **King sign:** does a positive-value king pin harder (smaller |close - king|/spot) than a negative-value king?
Method: hit rates with a binomial 95% interval; mean differences with a bootstrap 95% CI. 62 days x 2 symbols, and SPY and QQQ
are highly correlated, so the effective sample is closer to 62. Pilot only: a finding here gets a pre-registered setup and a
forward test, never a trade directly.
