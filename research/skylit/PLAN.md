# How we use Skylit (interactive review 2026-11-17)

Balance 103,885 credits (~$104). Credits are cheap; the limit is how much HISTORY each feed has.

## What we already know (don't repeat)
- Heatseeker gamma boards (king node, net gamma, accelerants): no pull, no range effect at 60 min, 90 min or to the close (pilots 1-2, 162 boards). Retired as a standalone signal.
- Tempest: next-day realized move is ~0.7x the priced move (variance premium), both halves. Live today: SPY trailing VRP avg 5.0, overpaid 94% of the last 252 days; QQQ 85%. A real, persistent edge, but it pays only through selling options, which the 5% cap blocks at $1,000 (LESSONS 37).

## Untested, ranked by testability (history / cost)
1. **Flux Field** (`flux_field`): Skylit's own buyer/seller control level with inner/outer/extreme bands. 1-min history for 30 sessions per call, 1 credit; daily for 252 days.
   - Test: long/short on reclaim/loss of the level, and fade or continuation on an outer-band tag. SPY and QQQ, both sides, through the foundry harness against the 1-min archive (fills next bar, costs, random control).
   - Build our own archive: pull the last session's 1-min Flux Field for SPY and QQQ every weekday (2 credits/day) so the sample keeps growing past 30 days.
2. **Market tide** (`market_tide`): market-wide net call / net put premium. Daily history ~360 days for 3 credits; 5-min intraday too.
   - Test: does net premium flow (day, or first hour) predict the rest-of-day or next-day SPY move? Use it as a gate on existing rules. Long archive (Alpaca) supplies prices.
3. **Flow tide / sweeps per ticker** (`flow_tide`, 3 credits per window): SPY/QQQ bullish vs bearish premium intraday. Same question as 2 at the ticker level.
4. **Tempest VRP / term structure as a day filter**: high realized-vs-implied days as a gate for trend rules (cheap, daily).
5. **Dark-pool top prints** as levels: last; level tests have failed before (LESSONS 26-28).

## Study window (Vivek, 2026-11-17)
- **Nov 18 to Dec 1: open budget** (soft cap 25,000 credits/week, balance stays above 50,000). Pull broadly: Flux Field 1-min (30 days, SPY/QQQ/TQQQ/SPXU/SQQQ/UPRO), market tide 5-min and daily, flow tide + sweeps for SPY/QQQ, Tempest VRP/skew/term daily, and rebuild a 30-day 0DTE heatmap history at 3-4 times a day if the cost per board allows. Cache everything.
- Goal: one Skylit-driven strategy that passes the pre-registered bar and goes on paper as desk `skylit_v1` (the first replacement slot).
- **From Dec 2: minimum mode.** Keep only the feeds the passing strategy (or the Coach's daily archive) needs; target < 100 credits/week. If nothing passes, Skylit drops to the Coach's 2-credit daily Flux Field pull and the Tempest VRP check.

## Rules of use
- Cache every pull on branch data under research/skylit/; never pay twice.
- Pre-register before computing; every rule gets long and short sides, both halves, and a random-entry control.
- Budget: see the study window above.

## Owners
- Researcher: tests 1-4 (Flux Field first, Wed Nov 18), pre-registered.
- Coach: daily Flux Field archive pull (2 credits) and a line in each post-mortem on where SPY/QQQ sat vs the level at each paper entry.
- Accountant: Skylit credits in the daily close, flagged if the weekly budget is passed.
