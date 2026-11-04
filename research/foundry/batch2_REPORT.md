# Foundry batch 2 + condor study 1: results (2026-11-04)

Pre-registrations: `PREREG_batch2.md` (commit 249a383) and `../skylit/PREREG_condor1.md` (+ amendment A), both committed before any result was computed.
- Code: `lab/foundry/batch2.py`, `lab/foundry/condor1.py`. No-look-ahead tests: `lab/tests/test_foundry_batch2.py`.
- Results: `research/foundry/batch2/summary.json`, `research/skylit/condor1_results.json`. foundry-lab now re-runs batch 2 every weekday.
- A = 1-min archive (27 sessions, Sep 28-Nov 3). B = 5-min archive (41 sessions, Sep 8-Nov 3). **A and B overlap on 27 sessions**, so "both archives" is weaker than two independent samples; B adds 14 earlier sessions.
- Net % per trade after 0.046% round-trip costs.

## Verdict: nothing passed. Four of five tests refuted; one weak support for a time cutoff.

### H1 giveback trail (exit at half of the best open profit, armed at +0.3% x leverage): refuted
| Entry set | n | GB − baseline per trade | 95% CI | Note |
|---|---|---|---|---|
| Paper-desk entries (1-min backtest, Oct 1-Nov 3) | 123 (GB fired 23) | +0.0015% | [−0.046, +0.054] | halves +0.029 / −0.023 |
| by desk | | volspike +0.18 (24), ema_vol −0.14 (17), ema_vol_v2 −0.11 (17), orb_vol 0.00, CVD 0 (never armed) | | |
| F1 cloud ride, A / B | 112 / 166 | −0.011 / −0.008 | | longs + , shorts − |
| F3 VWAP trend, A / B | 99 / 148 | −0.006 / +0.003 | | |
| Random entries, A / B | 59 / 88 | **−0.051 / −0.027** | [−0.131, +0.009] / [−0.078, +0.019] | worse on both sides on A |
The trail cuts winners as often as it saves givebacks. On random entries it is worse than holding. It looks good only on volspike, which is one desk out of six, and that is a selection after the fact.

### H2 trend-day gate at 10:30 ET: refuted
The gate picked 5 symbol-days on A and 12 on B.
| Rule | A: n / exp | B: n / exp | Ungated contrast A / B |
|---|---|---|---|
| G1 cloud ride on trend days | 7 / −0.228 | 20 / −0.048 | −0.027 / −0.052 |
| G2 tight cloud on trend days | 11 / −0.078 | 31 / −0.016 | −0.011 / −0.027 |
| G3 ride the 10:30 direction to 15:55 | 5 / −0.302 | 12 / −0.072 | G3x non-trend days +0.121 (29) / −0.043 (50) |
The "trend days" did not trend after 10:30. On these samples the first-hour direction does not continue. Longs lost and shorts won on both archives (G1 shorts +0.26% on B, n=7). That is the down-drift regime again (lesson 3), not the gate.

### H3 reversal day (0.6% leg, then the VWAP cross after 11:00): refuted
- A: 31 trades, +0.037%, CI [−0.108, +0.190], below the random 95th percentile (+0.148), −0.009% at 2x costs.
- B: 34 trades, +0.009%.
- The short side won (+0.11 / +0.07) and the long side lost (−0.05 / −0.06). Regime again.

### H4 entry-time buckets: the 13:00 ET cutoff is supported (weakly)
| Entries | before 11:30 | 11:30-13:00 | from 13:00 |
|---|---|---|---|
| Paper-desk backtest entries | 96 / +0.004 | 22 / +0.274 | **5 / −0.216 [−0.434, −0.104]** |
| Foundry trades, A | 223 / +0.043 | 115 / −0.055 | 88 / −0.075 [−0.130, +0.024] |
| Foundry trades, B | 331 / +0.010 | 180 / −0.062 | 166 / −0.068 [−0.107, −0.015] |
- The pre-registered 13:00 condition holds: the desk late bucket's CI is below 0, and the late bucket is negative on both archives. Paper adds its own 3 of 3 losses after 13:00.
- But the desk bucket is tiny. Its 5 trades are 4 independent ones, since ema_vol and ema_vol_v2 share one entry.
- The 11:30 cutoff is **not** supported for the desks: the desks' 11:30-13:00 trades did best.
- A cutoff makes late trades lose less. It does not create an edge: entries before 11:30 are about 0.
- **No new desk.** A cutoff desk would duplicate an existing desk on most days. The existing paper ledger already holds the forward test: the Saturday run tracks entries from 13:00 separately.
- Forward test, registered now: from Nov 5, **wrong if** paper entries from 13:00 ET have mean ≥ 0 after 10 trades.

### Condor study 1: 1-day SPY iron condor at ±1 priced sigma, $5 wings: refuted
- 21 condors, Oct 5-Nov 2, real Skylit last prices.
- At 1x costs: mean **−$12.52 per condor**, CI [−$72, +$35]. 81% won, but 4 breaches (19%) cost −$139 to −$427.
- Mean credit was only $0.48 against a $4.52 max loss.
- At 2x costs the mean is −$20.99. Even with no slippage it is −$4.04.
- The realized move was 0.68x the priced sigma, so the variance premium is real (lesson 5). The rounded 1-sigma condor still doesn't collect enough credit to pay for its tail.
- **Size check:** max loss is about $450 per condor, 45% of a $1,000 account. The 5% cap forbids this trade at live size anyway. One condor needs about $9,000 of equity, or about $1-wide wings.

## Variant count
9 batch-2 rules and exits plus 1 condor: 146 → 156.
Credits: 424 (84 × 5 contract_history, 3 for one truncated contract_chart, 1 Tempest); balance 104,533.
