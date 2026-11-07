# Foundry batch 3: opening-range break both sides, failed opening drive, prior-day levels, stale-high filter (pre-registered)

Written 2026-11-07 15:45 PT by the Researcher (Saturday review run), **before any result was computed**. Answers BOARD items coach 2026-11-05 (2), 2026-11-06/07 (1) and (2), and QUEUE 1b (prior-day high/low, opening drive). The Nov 5 and Nov 6 sessions that suggested H5/H6 are in both archives; they are named in the report so their weight can be judged (drop-them check below).

## Data
- A = 1-min archive `data:backtests/data/etf1m` (Sep 28 to Nov 6), SPY and QQQ, resampled to 5-min for decisions.
- B = 5-min archive `data:backtests/data/etf5m` (Sep 8 to Nov 6), SPY and QQQ.
- **Wick cleaning at ingest (new, BOARD coach 2026-11-05 (1), LESSONS 25):** a bar's high is clipped to max(o, c) x 1.004 when it is above that (low to min(o, c) x 0.996 when below) on 1-min bars; 1.006 / 0.994 on 5-min bars. The count of clipped bars is reported. All rules below use cleaned bars.
- Mechanics as batches 1-2: decide at a 5-min close, fill at the next 5-min open, flat at the 15:50 bar's close (15:55), costs 0.046% round trip on SPY/QQQ (2x stress 0.092%). Day-block bootstrap 95% CI. Halves = first/second half of each archive's sessions.
- Return is measured on SPY/QQQ in % (a paper desk would trade UPRO/TQQQ for longs and SPXU/SQQQ for shorts; LESSONS 6).
- Random control: same trade count, side mix and holding bars, random entry bars 09:45-15:30, 500 draws; the rule must beat the control's 95th percentile mean.

## H5 opening-range break, two-sided (ORB2)
- OR = high/low of 09:30-09:44 (the first three 5-min bars).
- Long: first 5-min close > OR high x (1 + buf). Short: first 5-min close < OR low x (1 − buf). One trade per side per day, at most one open position per symbol (first signal wins).
- Stop: the opposite side of the OR (long: OR low; short: OR high), capped at 1.0% from entry. Exit otherwise at 15:55.
- Grid, reported in full (6 cells): buf ∈ {0.10%, 0.30%} x entry window ∈ {before 11:00, before 11:30, until 15:25}.
- **Primary cell (the only one that can pass): buf 0.10%, before 11:00.** Reason: 0.10% is about 2x the round-trip cost, and the orb_vol paper losers were late entries (BOARD coach 2026-11-07 (2)).
- The window rows answer the orb_vol entry-window question: if the before-11:00 cell beats the until-15:25 cell on both archives, the breakout window should close earlier. That is a lesson for an `orb_vol_v2`, not an edit of `orb_vol`.

## H6 failed opening drive (FOD) and its continuation contrast
- Drive = (close of the 09:50 bar − 09:30 open) / open, i.e. the first 25 minutes.
- Drive day: |drive| ≥ 0.5% SPY or ≥ 0.7% QQQ (primary; QQQ moves about 1.4x SPY). Coach's 0.9% / 1.3% thresholds are reported as a second row (expect very few days).
- FOD (reversal): from 09:55 to 12:00, on the first 5-min close through the drive midpoint (midpoint of the 09:30 open and the session extreme in the drive's direction, as of that bar), trade against the drive. Stop: that session extreme as of entry. Exit otherwise 15:55. One trade per symbol per day.
- CONT (continuation contrast): on the same drive days, enter in the drive's direction at the 09:55 open; stop at the 09:30 open price; exit 15:55.
- The qualifying-day count and how many were continuation vs reversal days are reported before any P&L.

## H7 prior-day high/low
- PDH/PDL = prior session's regular-hours high/low from the same archive (the first session has none).
- HOLD (break-and-hold): 09:45-13:00, long after two consecutive 5-min closes above PDH (the first must be the first close above PDH that day); short mirror below PDL. Stop: PDH x (1 − 0.3%) for the long, PDL x (1 + 0.3%) for the short. Exit 15:55.
- REJ (reject): 09:45-13:00, after a 5-min high above PDH and then a close back below PDH within 3 bars, short; stop at the session high as of entry. Mirror long at PDL. Exit 15:55.
- One trade per rule per side per symbol per day.

## Pass bar (H5 primary, H6 FOD primary, H7 HOLD, H7 REJ: 4 candidates)
All of: net mean > 0 on both archives; archive A CI lower bound > −0.02%; both halves of B positive; above the random control's 95th percentile on B; net mean > 0 at 2x costs on B; long and short sides each ≥ 0 on B (a side with < 5 trades is stated as untested and cannot carry a pass); still > 0 on B with Nov 5 and Nov 6 dropped.
**If one passes:** a new paper desk key (UPRO/TQQQ long, SPXU/SQQQ short, `<rule>_v1`) per the charter. **Wrong if:** any condition fails.

## H8 stale-high filter (overlay, no new rule)
- At an entry's signal bar: a long is "stale" if the session high so far was made 15+ minutes earlier and the close is below VWAP; a short is stale if the session low is 15+ minutes old and the close is above VWAP.
- Applied to: (1) floor-lab paper-desk backtest entries (`data:backtests/floor/latest/trades_1m.csv`) on archive A 1-min bars; (2) random entries (both sides, 2 per symbol per day, held to 15:55 with a 0.5% stop) on A and B.
- **Supported** if stale entries' mean is below non-stale entries' mean in set (1) and in set (2) on both archives, for longs and shorts separately, and the day-block CI of (stale − non-stale) on B random entries is below 0. Supported ⇒ a lesson and a `_v2` desk proposal; desks are frozen.
- Also reported: the count of days with an extended impulse (|move from the open| ≥ 1.5% within the first 45 minutes, either archive), as asked in IDEAS 2026-11-04. Count only.

## Variants
H5 grid 6 + H6 FOD 2 thresholds + CONT 2 + H7 HOLD + REJ 2 + H8 filter 1 = 13. Running total 156 → 169.
