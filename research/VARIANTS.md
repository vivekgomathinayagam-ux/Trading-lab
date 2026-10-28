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
