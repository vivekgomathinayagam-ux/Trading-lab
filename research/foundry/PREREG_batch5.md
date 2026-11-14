# Foundry batch 5: profit-lock exit, CVD down-morning gate, H13 diagnostics, ORB first-break-only, regime check (pre-registered)

Written 2026-11-14 by the Researcher (Saturday review run), **before any result was computed**. Answers BOARD items coach 2026-11-11 (1), 2026-11-12 (1), 2026-11-13 (1) (profit lock), coach 2026-11-13 (2) (CVD gate), coach 2026-11-11 (2), 2026-11-12 (2), 2026-11-13 (1) (H13 splits) and QUEUE 1 (ORB first-break-only). All the leads came from sessions inside both archives, so a pass here only earns a paper desk under a new key, judged on sessions after it deploys.

## Data and mechanics (same as batch 4)
- A = 1-min archive `data:backtests/data/etf1m` (Sep 28 to Nov 13), SPY and QQQ resampled to 5-min. B = 5-min archive `data:backtests/data/etf5m` (Sep 8 to Nov 13).
- Wicks cleaned at ingest (0.4% on 1-min, 0.6% on 5-min). Decide at a 5-min close, fill at the next 5-min open, flat at 15:55. Costs 0.046% round trip (2x 0.092%). Day-block bootstrap 95% CI (2,000 draws). Halves = first/second half of each archive's sessions.
- Random entries: batch 4's set (3 random 5-min signal bars 09:45-15:05 per symbol per day, random side, seeds 21..28, stop 0.5%, else flat 15:55).
- Desk set: floor-lab desk backtest entries `data:backtests/floor/latest/trades_1m.csv` (Oct 1-Nov 13), measured on the traded symbol's 1-min bars (cleaned at 0.4% x leverage) resampled to 5-min. Index side: short for SPXU/SQQQ.
- Every rule family has a long and a short side; a one-sided result is LESSONS 24's regime until shown otherwise.

## H14 profit-lock exit (coach 2026-11-11/12/13, LESSONS 38; narrow retest of LESSONS 20)
- Paired variant on top of each trade's own exit. Armed once a bar's range after the fill reaches +ARM open profit on the traded instrument (long: high ≥ entry x (1+ARM); short: low ≤ entry x (1−ARM)). From the arming bar's close on, exit at the next 5-min open after the first 5-min close below the 5-min Ripster cloud's lower edge min(EMA5, EMA12) (short: above max(EMA5, EMA12)). EMAs on the traded instrument's 5-min closes, continuous across days, data up to that close only. The trade's own stop and the 15:55 flat still apply if they come first.
- ARM = 0.7% primary (the coach's level, absolute, not a fraction of MFE); 0.35% and 1.0% reported only, they cannot pass.
- Sets: random entries (A, B); H13 entries (A, B); ORB2_b10_w1100 and PD_HOLD entries (batch 3, A, B); the eod-holding desks in floor-lab (orb_vol, ema_vol, ema_vol_v2, volspike); and an H13-only cell.
- Report per set: n, n armed, base mean, PL mean, paired diff with CI, long/short, halves, and by day shape (batch 4's hindsight label; description only).
- **Supported** if all: paired PL − base > 0 on random entries on both archives, for longs and for shorts separately, in both halves of each archive; a CI above 0 on at least one archive; > 0 on the floor-lab desk set. **Refuted** if the pooled paired diff ≤ 0 on random entries on either archive. Otherwise inconclusive.
- If supported: a paper desk `volspike_pl` (volspike entries, this exit added), the only desk with a positive paper mean. Wrong on paper if its first 20 trades average below volspike's on the same days.

## H15 CVD down-morning gate (coach 2026-11-13 (2), LESSONS 39; not LESSONS 33's running-high filter, not H10's all-day 1%)
- Feature at the signal bar: QQQ's close / 09:30 open − 1 (data up to that close). A long is "gated" when the signal is before 10:30 ET and QQQ ≤ −0.5%; a short when before 10:30 and QQQ ≥ +0.5%.
- Early random set (deterministic, no seeds): every 5-min signal bar 09:45-10:25, both sides, SPY and QQQ, on every day. Primary exit: a 30-minute time exit (the CVD desks hold 3-33 min) with the 0.5% stop; eod hold reported. Gate on QQQ for both symbols (primary, as the coach wrote); own index reported.
- Desk set: floor-lab cvd_spy and cvd_tqqq entries (all long).
- **Untestable** if fewer than 20 gated early-random entries per side per archive.
- **Supported** if all: gated − ungated mean < 0 for longs and for shorts on both archives; the pooled CI entirely below 0 on at least one archive; the same sign in both halves of each archive; gated − ungated < 0 on the CVD desk set. **Refuted** if the pooled gated − ungated ≥ 0 on either archive. Otherwise inconclusive.
- If supported: a paper desk `cvd_tqqq_g` (cvd_tqqq with the long gate).

## H16 H13 diagnostics (descriptive only; H13's forward rule is unchanged)
- On the A and B H13 trades: by fill time (before 11:00 vs 11:00-14:05), with n and mean; stop reason mix.
- Paired variant: the stop is inactive for the first 3 bars after the fill (15 minutes); then the original stop applies (an already-breached stop exits at that bar's close).
- Forward count from `data:backtests/foundry/latest/batch4/h13_B_5m.csv`, days from Nov 12.
- Pre-stated reading: whatever these show, H13 stays a forward test judged by its first 15 new trades. A late-trigger or stop-timing effect can only become a separate pre-registered forward test.

## H17 ORB first-break-only (QUEUE 1, IDEAS 2026-11-07)
- Label each floor-lab `orb_vol` and `orb_plain` entry: first break if no 1-min close of the traded symbol after 09:45 was above the 09:30-09:45 opening-range high before the signal minute; otherwise a re-cross. Long ETF entries on SPXU/SQQQ are the short side.
- **Supported** if: re-cross mean < first-break mean in both desk sets, each cell with ≥ 5 trades, AND the first-break mean > 0 after costs in both sets. Otherwise no desk.
- If supported: paper desk `orb_vol_v2` (first break only).

## H18 regime check of LESSONS 24 (descriptive)
- Week of Nov 9-13 (SPY up on 4 of 5 days): batch 1 rule trades on B (`batch1_5m/trades.csv` as recomputed), long vs short mean on those days vs before Nov 9. If longs now win and shorts lose, 24's "shorts won" was regime, as stated.

## Variants
H14 3 arm levels + H15 1 gate (2 reported variants) + H16 delayed stop 1 + H17 1 = 6 counted (+2 reported) = 8. Running total 178 → 186.
