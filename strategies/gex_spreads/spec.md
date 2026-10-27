# GEX-filtered SPY/SPX vertical spreads — proposed spec (FOR REVIEW)

_Owner: Vivek Gomathinayagam. Drafted 2026-10-26 by Claude. **Status: idea — proposal only.** Nothing here is final trading logic. The bot does not load this setup (`stage: idea`; the registry runs only `paper` and `live`). No code, no deploy, no orders until Vivek reviews and answers the open questions at the bottom._

**How to read this:** every definition is tagged
- **[VERIFIED]** — the field exists in Skylit's API and was returned by a real call on 2026-10-26 (raw data shown below), or the rule is written in Vivek's own sources (FlowbyBobby rulebook / his notes).
- **[ASSUMPTION]** — my proposed formula or threshold. Not an established standard. Configurable in `config.yaml`. Vivek should confirm, change or reject it.
- **[VERIFY WITH SKYLIT]** — depends on how Skylit computes something it doesn't document (units, methodology). Needs checking against Skylit's docs or support before we rely on it.

---

## 1. What I checked before writing this

**Repo and notes:** `strategies/gex_spreads/` (only the four filter names, no definitions), `STATE.md`, `DECISIONS.md`, Vivek's trading-methods notes ("four-filter decision process (0DTE GEX share, IV ratio, pin score, net GEX regime)", originally built on FlashAlpha's 0DTE framework), and the FlowbyBobby rulebook Lessons 01–04 used by the `regime` skill. **None of these define a formula or threshold for any filter.** On 2026-10-26 Vivek listed five filters: 0DTE GEX, GEX Share, IV Ratio, Pin Score, Net GEX Regime. That's one more than his earlier four ("0DTE GEX share" is now two filters), so all definitions below are proposals.

**Skylit (live calls, 2026-10-26, ~22 credits ≈ $0.02):**

| Tool | What it returned (verified) | History | Cost |
|---|---|---|---|
| `heat_heatmap` | per strike: `strike`, `value` (signed), `nodeType` (king/gatekeeper/pika/barney/normal), `velocityPct*`; `spot`, `previousClose`, `asOf`. With `layout=matrix`: `matrix[strike][expiration]`, and each row sums to the strike's `value` (checked: strike 767 row sums to −161.97M = its value). | live only | 1 credit |
| `heat_levels` | the node list plus `summary`: `netExposure`, `flip.level`, `positiveWall`, `negativeWall`, `kingNode` | live only | 1 credit |
| `heat_historical_heatmap` | same per-strike shape at a past instant, **no matrix, no velocity, no summary**. Accepts `expirations` (e.g. only that day's 0DTE). Returned `asOf` 13:59:59Z for a request at 14:00:00Z, so there's no future leak. Tested at 2026-06-15 10:00 ET and 2025-11-03 10:00 ET. | **365 days back** | 5 credits |
| `tempest_iv` | `svx1d`, `svx9`, `svx30`, `svx3m`, `svx6m` (plain and `_adj` weekend-adjusted), `ratio_vix`, `term_slope`, `curve`, `iv_rank`, `iv_pct` | live | 1 credit |
| `tempest_history` | daily close rows: `svx1d`, `svx9`, `svx30`, `term_slope`, `em_1d_pct` (the 1-sigma move priced for the **next** session), `close`, more. Tested back to 2024-10-28. | **~2 years** | ~1 credit / 10 symbol-days |
| `option_chain` (historical date) | per strike: `callLastPrice`/`putLastPrice`, `callIv`/`putIv`, OI, volume, traded premium; `maxPain`. **End of day only: no bid/ask, no intraday price.** | past dates work | 3 credits |
| `contract_history` | daily per contract: `vwap`, `lastPrice`, `iv`, ask/bid/mid **execution volume split** (not quotes), OI change | past dates work | 5 credits |
| `contract_chart` | intraday bars for one contract. **Intraday buckets only reach 30 days back** (the API refused 135D). | 30 days intraday | 3 credits / 30D |

**Two data facts that shape everything below:**
1. **GEX history is 365 days.** That's shorter than the tournament's usual 2+ years. Results will be preliminary and cover roughly one market regime.
2. **Real intraday option prices exist only for the last 30 days.** A 0DTE spread entered at 10:00 ET a year ago can't be priced from a real quote. It has to be modeled (section 6, Stage B) or collected going forward.

## 2. Units and comparability — [VERIFY WITH SKYLIT]
- The `regime` skill treats `value` as dollars. Skylit's tool descriptions don't say **dollars per what move** (per 1% move? per $1 move? per point?).
- On the same night, SPY's King was −173M while SPXW's was −7.6M (both nearest expiry). SPX options carry far more notional than SPY, so Skylit is probably normalizing differently per symbol.
- **Rule for this spec:** never compare raw `value` across symbols, and never use a fixed dollar threshold. Every threshold below is a ratio, a sign, a distance in % or expected moves, or a percentile against that symbol's own history.

## 3. Architecture: raw metrics are separate from signals
```
Layer 1  RAW (stored as fetched, never edited)
         Skylit snapshots at fixed decision times → strikes[], values[], spot, asOf, expirations
         Tempest daily rows → svx*, em_1d_pct, term_slope
Layer 2  METRICS (pure functions of Layer 1, no thresholds)
         gex0_net, gex0_king, gex_share, iv_ratio, pin_score, net_gex, flip, regime_distance …
Layer 3  SIGNALS (metrics + thresholds from config.yaml → labels)
         e.g. pin_day = True, regime = "dampening", iv_state = "calm"
Layer 4  STRATEGY (signals → trade / no trade, structure, strikes, size)
         goes through the existing risk engine like every other setup
```
- Every metric and signal row keeps its source snapshot's `asOf`.
- Thresholds live only in `config.yaml`, so changing a threshold never touches metric code.
- Backtests log which threshold set produced each result, and every set tried is counted.

## 4. The five filters

Notation: board = the per-strike `value` list for one symbol at decision time *t*. **Window W** = strikes within ±`window_pct` of spot (assumption: ±1.5% for SPY and SPXW; configurable). Using a fixed % window instead of "the 92 strikes Skylit returns" keeps the metric stable when strike spacing differs (SPY $1, SPXW $5).

### 4.1 0DTE GEX — how much dealer gamma sits in today's expiry, and which way it leans
- **Intent:** 0DTE gamma decays within hours and drives intraday pinning or acceleration. This filter tells you whether today's expiry is a wall (dampening) or fuel (amplifying) near spot.
- **Inputs:** `heat_historical_heatmap` (live: `heat_heatmap`) with `expirations` = today's date [VERIFIED: works historically].
- **Raw metrics:**
  - `gex0_net` = Σ `value` over window W on the 0DTE-only board. Units: Skylit `value` units [VERIFY WITH SKYLIT].
  - `gex0_king_strike`, `gex0_king_value` = the strike with the largest |value| on the 0DTE board. This is our own computation (max |value|), which matches the rulebook's King definition [VERIFIED: rulebook]. We log Skylit's own `nodeType == king` alongside it as a cross-check.
  - `gex0_king_dist` = (king − spot) / spot, in %.
- **Derived signal [ASSUMPTION]:** `gex0_sign` = sign(`gex0_net`). Magnitude is judged as a **percentile of |gex0_net| over the trailing 60 sessions for that symbol** (strong ≥ 70th percentile, weak ≤ 30th). That avoids dollar thresholds.
- **Effect on trades:** positive and strong → pin playbook allowed. Negative and strong → trend playbook allowed. Weak → 0DTE map isn't driving the day; defer to Net GEX Regime.
- **Caveat [VERIFY WITH SKYLIT]:** does Skylit's gamma use start-of-day open interest, or does it update with intraday volume? If it's start-of-day OI only, 0DTE gamma at 10:00 misses positions opened that morning.

### 4.2 GEX Share — how much of the near-spot gamma is 0DTE
- **Intent:** if 0DTE dominates, intraday levels matter more. If longer-dated gamma dominates, the 0DTE King is a weaker reference.
- **Inputs:** two snapshots at the same *t*: the 0DTE-only board and the board over the nearest `share_expirations` expiries (assumption: 5, Skylit's default). Historically that's 2 calls (no matrix in history). Live, one `layout=matrix` call gives both [VERIFIED].
- **Formula [ASSUMPTION]:** `gex_share` = Σ_W |value_0DTE| / Σ_W |value_allN|. Units: fraction 0–1. **Absolute values** stop + and − strikes from cancelling. A signed version (`net0 / netN`) is logged too, but it's unstable when the denominator is near zero.
- **Threshold [ASSUMPTION]:** high ≥ 0.50, low ≤ 0.25 (configurable).
- **Effect on trades:** high → use 0DTE levels for strikes and targets at full size. Low → halve size or skip.
- **Example (real data, illustration only):** SPY after the close on Oct 26, nearest expiry (10-27) vs 5 expiries over 20 strikes: share = 0.39.
- **Alternative meaning (open question Q1):** "GEX Share" could instead mean King concentration, |King| / Σ|all values|. I've put concentration inside Pin Score (4.4). If Vivek meant concentration, the two filters swap.

### 4.3 IV Ratio — is today's option pricing calm or stressed
- **Inputs:** Tempest `svx1d_adj` and `svx30_adj` [VERIFIED fields]. History comes from `tempest_history` (~2 years) [VERIFIED].
- **Formula [ASSUMPTION]:** `iv_ratio` = `svx1d_adj` / `svx30_adj`. Front (1-day) implied vol relative to 30-day. Units: ratio.
  - Example (Oct 26 close, SPXW): 10.89 / 18.17 = 0.60. Plain, non-adjusted: 12.83 / 18.66 = 0.69.
  - Alternatives logged for comparison: `svx9/svx30`, `svx30/VIX` (`ratio_vix` field), `term_slope`.
- **Methodology [VERIFY WITH SKYLIT]:**
  - How Skylit builds SVX "constant-maturity IV" and its weekend adjustment isn't documented in the tool.
  - `term_slope` has no stated formula.
  - **Look-ahead rule:** a day's Tempest row is computed at that day's close, so a decision on day *t* may only use day *t−1*'s row (or a live intraday `tempest_iv` read, which isn't available historically).
- **Threshold [ASSUMPTION]:** calm < 0.80, normal 0.80–1.10, stressed > 1.10. Configurable. The alternative is percentiles of the ratio over the trailing 252 days.
- **Effect on trades:** calm → pin playbook favored (cheap front vol, quieter day priced). Stressed → event risk is priced, so skip the pin playbook. The trend playbook is allowed only if the regime is negative. Tempest's `em_1d_pct` (expected 1-day move, [VERIFIED]) also sets strike distances in 4.4 and section 5.

### 4.4 Pin Score — how likely price is to stick near one strike today
- **Intent:** a pin needs (a) a positive (wall) King, (b) price close to it relative to the expected move, and (c) gamma concentrated in that one node rather than spread out (a Rainbow Road board = no pin) [VERIFIED: rulebook concepts].
- **Inputs:** 0DTE board (4.1); `em_1d_pct` from the prior day's Tempest row.
- **Formula [ASSUMPTION]:**
  - `concentration` = |king| / Σ_W |value| (0–1)
  - `proximity` = max(0, 1 − |king − spot| / (spot × em_1d_pct/100 × `pin_em_mult`)), with `pin_em_mult` = 0.5 (assumption)
  - `pin_score` = 100 × 1[king value > 0] × concentration × proximity → 0–100
  - Distance is measured in expected moves, not a fixed %, so the score adapts to calm and volatile days.
- **Example (real data, illustration only):** SPY nearest expiry Oct 26: King 767 is **negative** (−173M), so `pin_score` = 0. A negative King is fuel, not a pin, even at only 0.08% from spot.
- **Threshold [ASSUMPTION]:** pin day ≥ 40. No pin < 15.
- **Alternatives logged:** Skylit's `maxPain` (from `option_chain`, but end-of-day only, so not usable at 10:00 historically), and Skylit's own `nodeType` labels (methodology undocumented [VERIFY WITH SKYLIT]).
- **Effect on trades:** high → pin playbook, with strikes placed around the King. Low → no pin trades.

### 4.5 Net GEX Regime — is the whole board dampening or amplifying
- **Inputs:** board over the nearest `share_expirations` expiries.
- **Raw metrics:**
  - `net_gex` = Σ_W value.
  - `flip` = the price where cumulative exposure, summed from the lowest strike up, changes sign (linearly interpolated between strikes).
  - `flip_dist` = (spot − flip) / spot.
- **What's verified:** Skylit's live `heat_levels.summary` has `netExposure` and `flip.level` [VERIFIED]. But it's computed "over the returned strikes", and there's **no historical version**, so for backtests we must compute our own.
- **Problem found:** on Oct 26 my flip over a 20-strike window came out at **758**, while Skylit's summary said **766.04**. The flip depends on the strike window, the expirations counted and the interpolation method. **Before use, our formula must reproduce Skylit's live flip on the same snapshots (open question Q4).**
- **Signal [ASSUMPTION]:**
  - dampening = `net_gex` > 0 and spot > flip + band
  - amplifying = `net_gex` < 0 and spot < flip − band
  - otherwise transition
  - band = 0.10% of spot (configurable)
  - Example: SPY Oct 26 net is negative but spot (766.36) sits only 0.04% above Skylit's flip, so it reads **transition**.
- **Effect on trades:** dampening → pin playbook allowed. Amplifying → trend playbook allowed. Transition → no trade, or edge fades only, matching the rulebook's "Conflict → wait" [VERIFIED: rulebook].

## 5. How the filters would combine — proposal, not final logic

All of these use **defined-risk verticals only**. No naked options, no margin (money rule 4).

| Playbook | Conditions (all thresholds are assumptions) | Structure (proposal) |
|---|---|---|
| **Pin** | regime = dampening, `pin_score` ≥ 40, `iv_ratio` < 1.10, `gex_share` ≥ 0.25 | credit vertical on the side away from the King, short strike beyond ±0.5 expected move from the King; or a debit vertical toward the King if spot is ≥ 0.5 expected move away |
| **Trend** | regime = amplifying, `gex0_sign` < 0 (strong), Trinity agrees (SPY and SPXW same side) | debit vertical in the direction of the break, target the next node, exit 1–3 strikes before it (Bobby's exit guideline [VERIFIED: rulebook]; its edge is unproven) |
| **Sit out** | transition regime, conflict between SPY and SPXW, `em_1d_event` = 1, CPI/FOMC days (Newsie flag), or concentration < 0.15 (Rainbow Road) | none |

**Account-size check (money rule 6), stated plainly:**
- Max loss per trade is 5% of live equity, which is **$50 at $1,000**.
- **SPX verticals don't fit:** a 5-point SPX vertical risks up to $500.
- **SPY $1-wide verticals fit** only when max loss is ≤ $0.50 per contract (debit ≤ $0.50, or credit ≥ $0.50 on a $1 width).
- So the live-tradeable version at $1,000 is **SPY only**. SPXW GEX would still be read as context (Trinity).

## 6. Backtest and validation plan (proposal)

### Stage A — do the filters predict what the underlying does? (no option prices needed; run first)
- **Data:**
  - Skylit historical boards at 10:00 ET and 12:30 ET (robustness) for the last ~250 sessions: SPY and SPXW, 0DTE-only and nearest-5.
  - Spot at 15:55 ET from one more snapshot.
  - Tempest daily history (day *t−1*).
  - Daily OHLC from Yahoo.
- **Outcomes** (from decision time to 15:55):
  - realized range ÷ `em_1d_pct`
  - |close − King| ÷ expected move
  - whether price crossed the flip
  - signed move
- **Test:** compare outcome distributions for filter "on" vs "off" days, with bootstrap 95% confidence intervals.
  - Thresholds are fixed before running (section 4 values), and the number of threshold sets tried is reported.
  - Time-ordered split: first ~8 months to look, last ~4 months untouched for out-of-sample.
- **Kill criterion (pre-registered):** stop before any options work if, on the out-of-sample months:
  - pin days don't show a smaller range/expected-move ratio and a closer finish to the King than all other days, and
  - amplifying days don't show a larger range than dampening days.
  - If either filter has no predictive value, no spread built on it will have an edge.
- **Cost:** about 4 calls × 5 credits × 250 days ≈ 5,000 credits (~$5) at 1 symbol per call. Possibly half if a multi-symbol call is still 5 credits [VERIFY WITH SKYLIT]. Tempest history is under 100 credits. That's within the ~$105 Skylit balance, and the Skylit plan is already paid, so this isn't new treasury spend.

### Stage B — spread P&L (only if Stage A passes)
- **Problem:** real intraday option quotes only exist for the last 30 days (section 1).
- **B1 Modeled prices (screening only, labeled as modeled):**
  - Black-Scholes with the strike's IV (from end-of-day `option_chain`/`contract_history` IV, or Tempest SVX) and the spot at decision time.
  - **Buy at modeled mid + half-spread, sell at mid − half-spread.** Half-spread assumption: $0.02 per SPY leg, run at 1×, 2× and 3×.
  - Plus the broker's per-contract fees (to verify against Tradier's and Robinhood's fee schedules).
  - Results must survive 2× costs.
- **B2 Real-price archive (starts on Vivek's yes):**
  - A daily GitHub Actions job saves 5-minute bars for the SPY 0DTE strikes near spot via `contract_chart` before they roll past 30 days.
  - It builds a real-quote dataset that grows every day. B1 results are re-checked against it as it fills.
- **Out-of-sample and walk-forward:** monthly rolling refits are allowed only for thresholds the section-4 rules let move (percentile windows). The last 3 months stay untouched until a single final run.
- **Gate to paper** (tournament rules): positive expectancy after 2× costs, profit factor ≥ 1.2, max drawdown ≤ 20%, beats SPY buy-and-hold on risk-adjusted return over the same days, and B1 roughly agrees with B2 on the overlap.

### Stage C — paper
- **Precondition:** paper fills need real-time option prices. Today the bot's options shadow fills use **delayed** Tradier sandbox quotes, which would make 0DTE paper results wrong.
- **Fix before paper:** price shadow fills from Skylit live data (chain/contract reads), or another real-time source. That touches the bot, so it needs Vivek's yes under money rule 9 if it touches order code.
- Then 50+ paper trades over 4+ weeks per the tournament gate.

### Look-ahead guards (all stages)
- Only use a snapshot whose `asOf` ≤ decision time.
- Use only day *t−1* Tempest rows for day *t*.
- No end-of-day `option_chain` fields (last price, maxPain) in a 10:00 decision.
- Unit tests prove these, like the crypto lab's no-look-ahead tests.

## 7. Open questions for Vivek
1. **GEX Share:** is it "0DTE share of total gamma" (4.2), or "King concentration"? Or both, with one living inside Pin Score?
2. **0DTE GEX vs Net GEX Regime:** should Net GEX Regime count only the nearest 5 expiries (my assumption), all expiries, or only 0DTE plus the next day?
3. **IV Ratio:** which pair did you use on FlashAlpha: 1-day vs 30-day, 0DTE ATM IV vs VIX, or something else? Any thresholds you already trade by?
4. **Flip level:** okay to require our computed flip to match Skylit's live `summary.flip` within 0.1% on 20+ snapshots before we trust it in backtests?
5. **Pin Score:** do you already have a formula from FlashAlpha? If so, I'll use yours and drop mine.
6. **Decision times:** is 10:00 ET the right first read (after the opening "amateur move")? Any other times you act on GEX?
7. **Structures:** credit verticals, debit verticals, or both? (Both are defined risk; credit spreads have assignment and early-exercise considerations on SPY, which is American-style; SPX is cash-settled but too big for $1,000.)
8. **Stage B2 archive:** okay to start saving SPY 0DTE intraday option prices daily from Skylit now (about 3 credits per contract per day, roughly 10 strikes ≈ 30 credits a day ≈ $0.03), so the real-price dataset starts growing?

## 8. Verified vs assumption — summary
| Item | Status |
|---|---|
| Per-strike gamma, signed, with node labels, live and 365 days back | VERIFIED |
| Per-expiration matrix (live only); rows sum to strike value | VERIFIED |
| `netExposure`, `flip`, walls (live summary only) | VERIFIED fields; computation window differs from ours (758 vs 766.04) |
| Units of `value`, and comparability across symbols | VERIFY WITH SKYLIT; treated as not comparable |
| Gamma from start-of-day OI vs intraday updates | VERIFY WITH SKYLIT |
| SVX tenors, `_adj`, `em_1d_pct`, `ratio_vix`, ~2 years of history | VERIFIED fields; SVX methodology and `term_slope` formula: VERIFY WITH SKYLIT |
| Intraday option prices only 30 days back; older is end-of-day only, no bid/ask | VERIFIED |
| King = largest absolute GEX; Pika = wall, Barney = fuel; Trinity 2-of-3; exit 1–3 strikes early | VERIFIED as Vivek's rulebook (not as a proven edge) |
| Every formula and threshold in section 4 | ASSUMPTION (configurable in `config.yaml`) |
| Playbooks in section 5 | ASSUMPTION / proposal |
| SPX verticals fail the 5% cap at $1,000; SPY $1-wide verticals with ≤$0.50 risk fit | VERIFIED arithmetic under money rules 5–6 |

_Data: Skylit. Estimated dealer positioning is context, not a signal or advice._
