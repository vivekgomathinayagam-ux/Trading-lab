# Research queue (ordered; the Researcher edits this)

_Last set: 2026-11-11 by the Researcher (Wednesday build run). Top item first._

## Now
- [x] Paper report script `lab/floor/paper_report.py` (2026-10-28, tested)
- [x] Parity replay `lab/floor/replay.py` (2026-10-28): Oct 26-27, 4/5 match, 1 explained (missing Yahoo bars -> `ema_vol_v2`)
- [x] CVD turn pre-registered, built, back-tested once, on paper from Oct 29 (`cvd_spy`, `cvd_tqqq`)
- [x] Skylit pilot 1 (10:00 ET boards, 62 days): no king pull, no gamma-sign effect on the rest-of-day move

- [x] Saturday Oct 31 review (2026-10-31): paper report, parity 10/16 match (stale-feed bug -> PR #2), weekly note `research/weekly/2026-W44.md`
- [x] Skylit pilot 2 (2026-10-31): 0DTE boards say nothing about the next 60-90 min; Tempest: realized next-day move ~0.7x the priced move (variance premium, both halves)

- [x] Foundry batch 2 + condor study 1 (2026-11-04, `research/foundry/batch2_REPORT.md`): giveback trail, trend-day gate, reversal day and the 1-day condor all refuted; 13:00 cutoff weakly supported (forward test on paper ledger). No desk changed.

- [x] Sat Nov 7 review (`research/weekly/2026-W45.md`): paper stats with CIs (43 trades, no desk at 20), parity 17/29 with one engine cause found (PR #3), C-2 boards Nov 2-6, batch 3 run early (two-sided ORB, opening drive, prior-day levels, stale-high filter): 0 of 4 passed.

- [x] Wed Nov 11 build run (`research/foundry/batch4_REPORT.md`): distance-from-extreme filter refuted, 1%-from-open filter inconclusive, fail-fast exit refuted, exits by day shape described (LESSONS 34-37); H13 1%-from-open continuation failed 2 of 7 conditions, now a forward test. Condor v2 blocked by the 5% cap at $1,000 (LESSONS 37).

1. **Sat Nov 14 review run:** paper stats with CIs (no desk at 20 yet; volspike nearest at 13), parity Nov 9-13, C-2 boards Nov 9-13 (5 calls), weekly W46; pre-register ORB first-break-only (`orb_vol_v2` candidate) on the desk replay, and a day-type marker test (IDEAS 2026-11-11). Check that foundry-lab ran batch 4 and H13 rows are accruing.
2. **Live-bar logging** in the bot (logging only; tests prove desks trade identically) so parity compares bar by bar. 3 of 6 parity gaps this week trace to Yahoo bar revisions that can't be proven without it.
3. **Run parity inside floor-lab** after the archive step (one more step in the Actions job; lab code only). Also make floor-lab's 5-min robustness table skip the CVD desks (3-min candles cannot be built from 5-min bars).
4. **Skylit forward collection** (also feeds combo C-2; until it exists, the Saturday run pulls the week's 10:00 ET 0DTE SPY/QQQ boards, 5 calls): `engine/skylit_feed.py` read-only snapshot at 09:45/10:30/12:30/15:00 ET for SPY, QQQ, SPXW (~20 credits/day) written to the ledger, so forward data accrues without paid backfills.
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
- **Entry follow-ups (2026-10-29):** (a) with Vivek's yes: shadow-log `ret_open_atr`, `dist_orh_atr`, `atr_pct`, frozen score per signal in the bot (no blocking); (b) with Vivek's yes: fix `CVDTurn.signal()` symbol check; (c) re-run `lab.floor.entry_lab` + `entry_analysis` at about 40 sessions, testing H1/H2 on new days only; (d) research the cvd_tqqq morning-reversal lead.

