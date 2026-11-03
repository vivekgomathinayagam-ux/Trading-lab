# Variant count

Every rule, parameter set and combination looked at, kept or not. Add a row each time.

| Date | Family | What | Kept? | Running total |
|---|---|---|---|---|
| 2026-10-25 | Floor day-trade | 3 paper desks + 3 comparisons (spec, pre-registered) | 3 paper | 6 |
| 2026-10-25 | Crypto Pier | 22 variants x 7 families x 2 coins (see crypto spec) + 16 short-horizon variants | none passed | see crypto spec |
| 2026-10-28 | Floor day-trade | `ema_vol_v2` (clock buckets; bug-fix version, pre-registered) | paper | 7 |
| 2026-10-28 | CVD turn | `cvd_spy`, `cvd_tqqq` (pre-registered, one backtest 1x/2x/3x costs) | 2 paper | 9 |
| 2026-10-28 | CVD turn (diagnostic, not desks) | same rule on QQQ, UPRO, SQQQ, SPXU, run after seeing the TQQQ result | none | 13 |
| 2026-10-28 | CVD turn controls | long 09:48->15:55 same days; random same-duration entries 09:48-10:40 | controls | 13 |
| 2026-10-28 | Skylit pilot 1 | 3 questions on 10:00 ET GEX boards (king pull, net-gamma sign vs move, king sign vs pin) | none held up | 16 |
| 2026-10-28 | Combo | C-1 cvd_tqqq + volspike confluence (record only) | registered | 17 |
| 2026-10-29 | Exit study (entries frozen) | 18 exit variants (6 fixed TP, 3 trail, 2 ATR trail, 3 partial, 4 CVD delay/confirm) x 5 desks + random-entry control + overnight-hold check; none adopted | none | 35 |
| 2026-10-29 | Entry-quality study (research only) | 196 feature correlations, 3 regime dims, 1 score + 12 ablations, 15 filters/combos x 6 desks (90 configs), 3 post-hoc checks; no filter passed the train+validation bar | none | 129 |
| 2026-10-31 | Skylit pilot 2 | 0DTE boards 10:00/12:30 ET: magnet pull, gamma sign vs range, accelerant proximity (each at 60 and 90 min) + Tempest priced-vs-realized move and term slope | none tradeable; variance premium noted as a lead | 137 |
| 2026-10-31 | Combo | C-2 volspike split by SPY 0DTE net gamma at 10:00 (record only, forward from Nov 2) | registered | 138 |
| 2026-11-03 | Foundry batch 1 | F1 cloud ride, F2 cloud ride tight, F3 VWAP trend, F4 trend break, F5 Fib 61.8, F6 Fib 38.2 (both sides each) + C1 long 09:45 + C2 random control; 1-min (26 sessions) and 5-min (41 sessions) | none passed; all refuted on 41 sessions | 146 |
