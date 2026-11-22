# Foundry batch 7 (Sat 2026-11-21 review run)

Pre-registered in `PREREG_batch7.md` (commits 691aa6d, 715bdf9) and `PREREG_volspike_grid.md` (11-18). Development results frozen in commit 5627ed2 before the 2026 holdout was opened. Code `lab/foundry/batch7.py`, tests `lab/tests/test_foundry_batch7.py` (fast replay = `lab.floor.engine.simulate` trade for trade; MA features unchanged when the data is cut at the signal; mirrored inverse filters). Results: `research/foundry/batch7/` (dev.json, holdout.json, grid_dev.csv, h27.json).

**Data:** Alpaca 1-min (SIP), SPY QQQ TQQQ UPRO SQQQ SPXU, 2022-01-06 to 2026-11-18: 1,000 development sessions (2022-2025) and 222 holdout sessions (2026). Splits back-adjusted (TQQQ 2:1 2022-01-13 and 2025-11-20, UPRO 2:1 2022-01-13, SQQQ 1:5 three times, SPXU 1:5 / 1:4). Statistic: P&L per trade in % of a $1,000 desk, after the spec's slippage; 2x = double slippage. Check on real data: on Mar-May 2024 the fast replay and the engine agree on every entry, symbol and exit reason (moves differ by ≤ 0.01 from rounding).

**Verdict: 0 of 5 hypotheses passed. None of the four paper desk rules has an edge on 1,222 sessions, and no MA filter, volume gate, slot design or Tempest gate gives them one.**

## Volspike MA grid (Vivek's request, 2026-11-17)
- Correction: the 11-18 pre-registration counted 1,190 variants; the grid as written is **924 filters + base** (2 views x 3 timeframes x 2 MA types x (11 lengths x 2 tests + 55 pairs)); 2x11x3x2 is 132 singles, not 264. Multiple-testing figures use 924.
- Base volspike, development: 996 trades, **+0.035% [−0.068, +0.138]**, 2022-23 +0.145, 2024-25 −0.073, 2x costs −0.041, 37 targets / 151 stops.
- 590 of 924 filters have a positive development mean, but the best improvement (+0.022, `own|5m|SMA8>SMA9`) is **below the 95th percentile of 924 random filters (+0.024)**: 0 filters beat chance. Top filter one-sided Welch p = 0.38, Bonferroni p = 1.0.
- Holdout 2026 (opened once): base **−0.095% [−0.29, +0.08]** (222); top 3: SMA8>SMA9 −0.142, EMA200 slope −0.043, SMA34>SMA50 −0.164. None beats chance, none is positive. **No `volspike_v2`. The family is refuted.**
- By year (base): 2022 +0.171, 2023 +0.120, 2024 −0.125, 2025 −0.020, 2026 −0.095. Volspike made money in the 2022 bear market and has not since.

## H25: the volume gate (coach, BOARD 11-19 / 11-20)
Development mean per trade (long side = SPY/QQQ/TQQQ/UPRO desk, short = SQQQ/SPXU desk):

| Rule | 3x long | 1.5x long | none long | 3x short | 1.5x short | none short |
|---|---|---|---|---|---|---|
| ORB | −0.008 (433) | −0.002 (690) | −0.001 (816) | −0.017 (424) | −0.125 (636) | −0.087 (792) |
| EMA 9/21 | −0.051 (529) | −0.030 (754) | −0.004 (860) | −0.072 (448) | −0.106 (674) | −0.078 (838) |

- All 12 cells are ≤ 0 on development; all CIs include 0; all are negative at 2x costs. Holdout: 9 of 12 negative; the 3 positive (ORB short 3x +0.063, 1.5x +0.071; EMA short 3x +0.015) have CIs from −0.2 to +0.37.
- Neither registered prediction holds cleanly (the gate is not better in both halves and both sides; "none" is not better everywhere either). Reading: **the gate changes how many trades a rule takes, not whether it has edge.** No desk.
- Answer to the coach (Nov 20 10:19): from the bot's own bar log, SQQQ's range-high cross had a 1.32x volume ratio and SPXU's 2.50x (median of the prior 20 bars, the engine's measure), so the 3x gate blocked orb_vol. Nov 18: SPXU 09:47 1.17x, SQQQ 09:48 0.79x, blocked; the first 3x cross was SPXU 12:11 at 7.33x, which is the paper 12:12 fill. Nothing else blocked it.

## H26: one slot per side (coach, BOARD 11-20 item 1)
Per signal-session P&L, development: ORB plain one slot +0.024 vs two slots −0.069; EMA plain −0.020 vs −0.075; volspike +0.035 vs −0.089. Holdout the same sign (−0.12 vs −0.17, −0.02 vs −0.11, −0.10 vs −0.22). The second slot adds trades that lose. **Refuted.** Nov 20's SQQQ miss was one day; over 1,000 days the blocked trades are worse than the ones taken.

## H27: Tempest term structure as a side gate (Skylit PLAN item 4)
Tempest daily history SPY/QQQ 2024-10-01 to 2026-11-20 (538 rows each, ~170 credits, cached at `data:research/skylit/tempest/`). Stress = prior-close SPY term slope > 0 (15% of days).
- Gate (stress → inverse ETFs only, calm → bull only), SPY slope: volspike −0.148 vs −0.075 base (469 / 534), ORB 3x −0.056 vs −0.013, EMA 3x −0.105 vs −0.041. **Worse on all three; refuted.**
- Reported cells: QQQ slope gate on ORB 3x +0.073 [−0.10, +0.24] (216), both halves positive (+0.13 / +0.01), 2x +0.008. One positive cell in 9 looked at, CI includes 0: noise until shown otherwise; not a lead to trade.
- "Calm days only" does nothing (−0.074 vs −0.075 volspike).

## H28: +5% target vs holding to 15:55 (coach IDEAS 11-20 / 11-21)
Same entries, paired per trade, inverse-ETF trades (the cell the coach asked about): volspike hold − target +0.023 [−0.03, +0.08] (469 dev), but −0.033 in 2022-23, +0.073 in 2024-25 and −0.030 on the 2026 holdout; ORB 3x +0.023 [−0.02, +0.07] (holdout 0: no targets hit in 2026); EMA 3x +0.004; ORB plain −0.007. All trades: +0.006 to +0.018, every CI includes 0. **Refuted:** the two Nov 19-20 trades where holding would have doubled the gain are real, but over 1,000 sessions the target costs about nothing, because it is hit on only 2-5% of trades and holding the rest gives back as often as it gains. Keep the spec's target.

## What this says about the paper desks (long-archive replay of their exact code, 2022-01-06 to 2026-11-18)

| Desk rule | Trades | Mean % / trade (95% CI) | 2x costs | +5% targets |
|---|---|---|---|---|
| volspike | 1,218 | +0.012 [−0.080, +0.101] | −0.065 | 39 (3.2%) |
| orb_vol (ORB 3x) | 810 | +0.028 [−0.071, +0.128] | −0.053 | 20 (2.5%) |
| ema_vol (EMA 3x) | 874 | −0.045 [−0.123, +0.035] | −0.114 | 13 (1.5%) |
| orb_plain | 1,222 | −0.002 [−0.091, +0.087] | −0.061 | 47 (3.8%) |
| volspike_2x | 1,221 | +0.041 [−0.057, +0.140] | −0.030 | 58 (4.8%) |

Zero edge after costs for every desk; the paper results (volspike +0.54%/trade on 20) are within this noise and carried by down weeks. Over the paper window itself (Oct 26-Nov 18) the Alpaca replay of volspike made +0.24%/trade on 18 trades, the same picture.

**Targets by side (LESSONS 1 split):** inverse ETFs hit +5% on 27 of 569 volspike trades (4.7%), 17/414 ORB 3x (4.1%), 44/583 ORB plain (7.5%); bull side 12/649, 3/396, 3/639 (0.5-1.8%, most of them TQQQ/UPRO). Reachable on 3x inverse entries on fast down days; still rare overall.

## Variants
Grid 925 (924 + base), H25 12, H26 3 new, H27 3 + 6 reported, H28 4 = 953 this batch; running total 1,165.
