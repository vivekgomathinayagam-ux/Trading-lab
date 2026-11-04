# Foundry batch 2: giveback trail, trend-day gate, reversal day, entry-time cutoff (pre-registered)

Written 2026-11-04 15:50 PT by the Researcher, **before any result was computed**. Answers four BOARD items (coach 2026-11-03 x2, interactive 2026-11-03 x2).

## Data (same as batch 1)
- A = 1-min archive `data:backtests/data/etf1m` (Sep 28 to Nov 3, 27 sessions; SPY, QQQ, TQQQ, UPRO, SQQQ, SPXU).
- B = 5-min archive `data:backtests/data/etf5m` (Sep 8 to Nov 3, 41 sessions; SPY, QQQ).
- Shared mechanics, costs (0.046% round trip on SPY/QQQ; 0.106% on the 3x ETFs = 0.05% slip + 0.003% fee per side), next-bar-open fills, flat by 15:55, max 3 trades/rule/symbol/day, day-block bootstrap: as batch 1.
- Halves = first and second half of each archive's sessions.

## H1 giveback trail (exit overlay; entries frozen)
**Exit GB:** once open profit (from bar highs for a long, bar lows for a short) reaches the arm level, exit at the next bar's open after a bar *closes* with open profit at or below half the best so far. Arm = 0.3% x leverage (0.3% SPY/QQQ, 0.9% for 3x ETFs). All the entry set's own exits still apply; GB only adds an earlier exit.
**Entry sets:**
1. Paper-desk entries from floor-lab's 1-min backtest (`data:backtests/floor/latest/trades_1m.csv`: orb_vol, ema_vol, ema_vol_v2, volspike, cvd_spy, cvd_tqqq), simulated on archive A 1-min bars. Desks are long-only; the inverse-ETF trades are their short side.
2. F1 cloud ride and F3 VWAP trend entries (both sides), archives A (5-min resample) and B.
3. Random entries (both sides, 09:45-15:00 ET, 2 per symbol per day, seed 21), held to 15:55 with a 0.5% hard stop, archives A and B. This is the "does the exit itself add anything" test.
Comparisons: own exit (baseline) vs own exit + GB; for set 3 also hold-to-15:55 vs GB.
**Pass (adopt GB):** paired difference (GB − baseline) per trade > 0 in set 1 pooled, with day-block bootstrap CI lower bound > 0, AND positive in both halves of set 1, AND positive point estimate for longs and shorts in set 3 on both archives. 2x costs: trade count is unchanged, so costs cancel in the paired difference; reported anyway.
**If it passes:** new paper desks `<desk>_gb` for at most 2 desks (the cap is 8). Existing desks untouched.
**Wrong if:** set-1 CI includes 0, or set 3 is negative on either side.

## H2 trend-day gate at 10:30 ET
Decided at the close of the 10:25 5-min bar (data 09:30-10:29 only).
- Rng = (high − low) / open of 09:30-10:29; RVol = volume 09:30-10:29; both vs the median of the prior 10 sessions (first 10 sessions are warm-up, not traded).
- Dir = sign(close 10:29 − VWAP 10:29). Slope = VWAP(10:29) − VWAP(09:50) must have the same sign. Dist = |close − VWAP| / VWAP ≥ 0.10%.
- **Trend day** = Rng ≥ 1.2x median AND RVol ≥ 1.0x median AND slope agrees AND Dist ≥ 0.10%.
Rules (5-min decisions, SPY and QQQ):
- G1: F1 cloud-ride entries after 10:30, only on trend days, only in Dir; F1 exits.
- G2: F2 likewise; F2 exits.
- G3: enter at the 10:30 bar's open in Dir on trend days; exit 0.5% hard stop or 15:55.
- G3x (contrast, not a candidate): the same G3 trade on non-trend days, Dir as defined.
**Pass:** on both archives net exp > 0; archive A CI lower > −0.02%; both halves positive on B; beats the random control (95th pct); survives 2x costs; G-rule mean above its ungated version (F1/F2 after 10:30 all days; G3 vs G3x). Long and short sides reported separately; a pass needs both sides ≥ 0 on B, or a side with < 5 trades stated as untested.
**If it passes:** a paper desk trading UPRO/TQQQ for long Dir and SPXU/SQQQ for short Dir (desks are long-only), new key `trendday_v1`.

## H3 reversal day (coach idea)
- R1 short: after 11:00 ET and before 14:30 ET, if the session high was made after the session low and (high − low)/low ≥ 0.6% by then, short on the first 5-min close below VWAP. Mirror long: low after high, range ≥ 0.6%, first close above VWAP.
- Exit: stop at the session extreme as of entry (short: session high), else 15:55. One trade per side per day.
- Same pass bar as H2 (no gate comparison).

## H4 entry-time cutoff (analysis, no new rule)
On paper-desk backtest entries (set 1) and on all batch-1 + batch-2 foundry trades: net exp per trade by entry bucket: before 11:30, 11:30-13:00, from 13:00 ET.
**Cutoff "13:00" supported** if the ≥13:00 bucket mean is < 0 with CI upper bound < 0 in the pooled desk entries AND negative on both foundry archives. "11:30" likewise for the ≥11:30 buckets combined. Supported ⇒ a lesson and, for the desks, a `_v2`-style key proposal (desks are frozen).

## Variants
GB exit 1 + hold-to-15:55 1, G1-G3 3 + G3x contrast 1, R1 1, cutoffs 2 = 9, plus controls. Running total 146 → 155.
