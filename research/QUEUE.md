# Research queue (ordered; the Researcher edits this)

_Last set: 2026-10-28 by the Researcher (Wednesday build run). Top item first._

## Now
- [x] Paper report script `lab/floor/paper_report.py` (2026-10-28, tested)
- [x] Parity replay `lab/floor/replay.py` (2026-10-28): Oct 26-27, 4/5 match, 1 explained (missing Yahoo bars -> `ema_vol_v2`)
- [x] CVD turn pre-registered, built, back-tested once, on paper from Oct 29 (`cvd_spy`, `cvd_tqqq`)
- [x] Skylit pilot 1 (10:00 ET boards, 62 days): no king pull, no gamma-sign effect on the rest-of-day move

1. **Saturday Oct 31 review**: paper report + parity for Oct 26-30, first look at the 3 new desks (expect 2-3 trades each; nothing to judge).
2. **Run parity inside floor-lab** after the archive step (one more step in the Actions job; lab code only). Also make floor-lab's 5-min robustness table skip the CVD desks (3-min candles cannot be built from 5-min bars).
3. **Skylit edge study, pilot 2** (pre-register first): intraday horizon instead of rest-of-day. Boards at 10:00/12:30 ET vs the next 60-90 minutes from the 1-min archive (Sep 28 on): distance to the nearest large positive node (magnet) and to the nearest large negative node (accelerant); 0DTE-only board (max_expirations=1). Also Tempest: SVX/IV term slope vs next-day range (cheap: tempest_history).
4. **Skylit forward collection**: `engine/skylit_feed.py` read-only snapshot at 09:45/10:30/12:30/15:00 ET for SPY, QQQ, SPXW (~20 credits/day) written to the ledger, so forward data accrues without paid backfills.
5. **Skylit edge study (continuing)**:
   - Map which Skylit tools have history and how far back.
   - Build a cached dataset on branch `data` (`research/skylit/`): GEX boards at fixed decision times (09:45, 10:30, 12:30, 15:00 ET) for SPY/QQQ/SPXW, plus Tempest daily rows.
   - Measure what each feature predicts for the next hours on SPY/QQQ and the 3x ETFs: King-node pull and pins, flip distance, gamma sign vs realized range, wall rejections, IV term structure.
   - Look ahead only at data whose asOf is at or before the decision time.
   - Write findings in the weekly note.
6. **Skylit paper desks**: pre-register 1-3 ETF day-trade setups built from what step 5 found, back-test once, then build `engine/skylit_feed.py` (read-only) and put them on paper.

## Next
7. First pre-registered combos (`research/combos.md`): portfolio of the three paper desks, drop-one, GEX regime as a gate on each day-trade desk. Judged on forward days only.
8. Option spreads from Skylit signals: model-priced first (2x cost stress). Paper needs real-time option prices and an options order path; the order path is `engine/` order code, so it goes to Vivek as one PR plus one City Hall item.
9. New-setup ideas from the CHARTER list, one per week, pre-registered.

## Standing
- Weekly: check the crypto-lab run succeeded (Sat 09:17 UTC); fix lab code if it broke. Pier research only when the Floor queue is empty.
- No open questions for Vivek. The Researcher defines every GEX and Skylit metric itself (Vivek, 2026-10-26).
- **Exit follow-ups (2026-10-29):** (a) clone desks `cvd_tqqq_atr2`, `cvd_spy_atr3` once Vivek says yes (new classes only; engine untouched); (b) re-run `lab.floor.exit_lab` at about 40 archived sessions and on Month-1 paper trades.

