# Research queue (ordered; the Researcher edits this)

_Last set: 2026-11-25 by the Researcher (Wednesday build run). Top item first._

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

- [x] Sat Nov 14 review (`research/weekly/2026-W46.md`, `research/foundry/batch5_REPORT.md`): paper 63 trades, no desk at 20; parity 17/24 (gaps = bar revisions); batch 5: profit lock and ORB first-break refuted, CVD down-morning gate inconclusive, H13 forward 0/4; long/short flipped with the tape (LESSONS 24). C-2 boards skipped (Skylit connector needs reconnecting). No desk change.

- [x] Wed Nov 18 build run (`research/foundry/batch6_REPORT.md`): first tests on the long Alpaca archive (1,729 sessions). H13, the 0.5% morning continuation, the 13:00 cutoff and the first-hour day-type marker all flat over 6 years; Skylit daily market tide refuted; Flux inner-band gate right sign but CI includes 0 (29 sessions). Skylit cache: Flux 1-min 30 sessions SPY/QQQ + market tide 360 days (~200 credits). Volspike MA grid pre-registered; 1-min Alpaca pull added to alpaca-history. 0 of 6 passed; no desk change.

- [x] Sat Nov 21 review (`research/weekly/2026-W47.md`, `research/foundry/batch7_REPORT.md`): paper 78 rows, volspike 20 trades +0.54 [−0.10, +1.24], no desk retirable; parity 6/6 bar by bar since PR #3; Newsie 3-day shadow (caution +$14.40, bias +$5.14); volspike MA grid (924 filters) refuted; volume gate, per-side slot, Tempest side gate, target-vs-hold all refuted; the four paper desks' own code has ~0 expectancy on 1,222 Alpaca sessions (LESSONS 49). Tempest history cached (~170 credits).

- [x] Wed Nov 25 build run (`research/foundry/volguard_REPORT.md`, `research/foundry/batch8_REPORT.md`): the coach's urgent data fault came first: running-volume guard shipped on paper (LESSONS 56 confirmed, 11 independent paper trades through Nov 20 fired on such bars), early-close handling shipped (Nov 27, Dec 24); batch 8: V days too rare (LESSONS 58), impulse fade refuted (57); Newsie 6-day shadow. **Not done, carried:** news-scalper harness and the Alpaca news query, first-hour market tide, Flux first-tag test (coach 11-24 item 2).

1. **Sat Nov 28 review + Month-1 report** (see Next): paper stats with and without the 12 running-volume trades; parity on the bar log; first half-day (Nov 27) check.
1b. **Wed Dec 2 build run:** (a) news-scalper harness with the historical Alpaca news query fixed first (overdue twice); (b) Flux first-tag fade with the coach's first-tag definition (IDEAS 2026-11-24), 30+ cached sessions, both sides, vs random; strike the clause in LESSONS 48 if it fails; (c) Skylit minimum mode from Dec 2 (< 100 credits a week).
~~1-old.~~ (superseded 2026-11-25 by 1 and 1b) **Wed Nov 25 build run (the desks have no edge; look for a different source):** (a) news-scalper harness, historical Alpaca news query fixed first (Vivek's item 3, overdue); (b) Skylit study last day Nov 24 is past by Wednesday: if possible pull the intraday 5-min market tide (first hour) before then, else note it missed the window; test tide-in-first-hour vs rest-of-day on SPY/QQQ (pre-register); (c) Flux extreme-band tag, slope/side split (coach 11-18, 11-19); (d) an inverse-ETF-only trend rule judged on 2022 and 2024 separately; (e) structural stop beyond the mid-morning bounce (coach 11-16) and the H12 by-symbol re-cut (coach 11-17) on the long archive. Long archive first (Alpaca 1-min for ETF rules, 5-min from 2020 for SPY/QQQ).
2. ~~**Live-bar logging**~~ (done 2026-11-17, `ledger/daytrade_bars_<day>.csv`) in the bot (logging only; tests prove desks trade identically) so parity compares bar by bar. 3 of 6 parity gaps this week trace to Yahoo bar revisions that can't be proven without it.
3. **Run parity inside floor-lab** after the archive step (one more step in the Actions job; lab code only). Also make floor-lab's 5-min robustness table skip the CVD desks (3-min candles cannot be built from 5-min bars).
4. **Skylit forward collection** (also feeds combo C-2; until it exists, the Saturday run pulls the week's 10:00 ET 0DTE SPY/QQQ boards, 5 calls): `engine/skylit_feed.py` read-only snapshot at 09:45/10:30/12:30/15:00 ET for SPY, QQQ, SPXW (~20 credits/day) written to the ledger, so forward data accrues without paid backfills.
5. **Skylit edge study (continuing; study week Nov 18-24, 10,000-credit cap, ~200 used by Nov 18)**: next pulls: intraday 5-min market tide (first hour), flow_tide SPY/QQQ, Tempest dailies as a day filter; Flux re-run at 60 sessions.
   - Map which Skylit tools have history and how far back.
   - Build a cached dataset on branch `data` (`research/skylit/`): GEX boards at fixed decision times (09:45, 10:30, 12:30, 15:00 ET) for SPY/QQQ/SPXW, plus Tempest daily rows.
   - Measure what each feature predicts for the next hours on SPY/QQQ and the 3x ETFs: King-node pull and pins, flip distance, gamma sign vs realized range, wall rejections, IV term structure.
   - Look ahead only at data whose asOf is at or before the decision time.
   - Write findings in the weekly note.
6. **Skylit paper desks**: pre-register 1-3 ETF day-trade setups built from what step 5 found, back-test once, then build `engine/skylit_feed.py` (read-only) and put them on paper.

## Next
- **Month-1 report, Sat Nov 28** (`research/reports/2026-11-month1.md`), with a separate agent re-deriving every number from the raw ledger and `data:validate-data`. Apply the retirement rule to any desk at 20+ trades, and decide the paper slots after the frozen month with LESSONS 49 in view (replay of each desk's code on 2022-2026 next to its paper stats). Publish as a doc and link it from City Hall.
7. First pre-registered combos (`research/combos.md`): portfolio of the three paper desks, drop-one, GEX regime as a gate on each day-trade desk. Judged on forward days only.
8. Option spreads from Skylit signals: model-priced first (2x cost stress). Paper needs real-time option prices and an options order path; the order path is `engine/` order code, so it goes to Vivek as one PR plus one City Hall item.
9. New-setup ideas from the CHARTER list, one per week, pre-registered.

## Standing
- Weekly: check the crypto-lab run succeeded (Sat 09:17 UTC); fix lab code if it broke. Pier research only when the Floor queue is empty.
- No open questions for Vivek. The Researcher defines every GEX and Skylit metric itself (Vivek, 2026-10-26).
- **Exit follow-ups (2026-10-29):** (a) clone desks `cvd_tqqq_atr2`, `cvd_spy_atr3` once Vivek says yes (new classes only; engine untouched); (b) re-run `lab.floor.exit_lab` at about 40 archived sessions and on Month-1 paper trades.
- **Entry follow-ups (2026-10-29):** (a) with Vivek's yes: shadow-log `ret_open_atr`, `dist_orh_atr`, `atr_pct`, frozen score per signal in the bot (no blocking); (b) with Vivek's yes: fix `CVDTurn.signal()` symbol check; (c) re-run `lab.floor.entry_lab` + `entry_analysis` at about 40 sessions, testing H1/H2 on new days only; (d) research the cvd_tqqq morning-reversal lead.

