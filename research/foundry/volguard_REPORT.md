# Running-volume guard (LESSONS 56): check and effect (Researcher, 2026-11-25)

Answers BOARD 2026-11-24 coach item 1 (a)-(c). Code: `strategies/daytrade/core.py` (`Features(vol_guard=True)`, `running_volume_mask`), `lab/foundry/rules.py` (`load_bars(clean_volume=True)`), tests `tests/test_volume_guard.py`. Scripts used for the numbers below: `lab/foundry/volguard_impact.py`.

## The fault
Yahoo sometimes sends a 1-min bar whose volume is the session's running total. On the bot's own bar log (Nov 18-25) the first such bar of a run is 1.01-1.14x the session's volume so far, and later ones keep tracking the running total. QQQ has them every day (10-28 a day), TQQQ most days, SPY/UPRO rarely.

## The rule (one parameter set, chosen from 6 looked at)
A bar's volume is treated as missing when it is more than **20x the median of the prior 20 clean bars** AND at least **0.5x today's clean volume so far** (and at least one earlier bar today). Missing means: no volume spike on that bar, and the bar is kept out of the 20-bar baseline, the same-minute history and VWAP. Prices are untouched. The flagged bar is judged from earlier bars only (no look-ahead).

Why 0.5 and not the coach's 0.8 with a 09:45 start: with 0.8, one bad bar that slips through (Oct 12 09:35, 11x) enters the running total, and every later bad bar that day is then only half of it, so the whole day slips (284 bad bars missed on the Yahoo archive). With 0.5 from the second bar: 158 missed, almost all 09:30 bars (Yahoo's open bar includes the auction; Alpaca's does not, so that is a provider difference, not this fault) and 15 bars over 20x.

| candidate | Alpaca 1-min 2022-26 flags (all 6 ETFs) | Yahoo bad bars caught | Yahoo bad bars missed | Yahoo flags that were not bad |
|---|---|---|---|---|
| 20x / 0.8 / from 09:40 (coach) | 7 | 1,269 | 284 | 0 |
| **20x / 0.5 / from 09:31 (shipped)** | **139** | **1,395** | **158** | **2** |
| 20x / no share test / from 09:40 | 4,849 | 1,389 | 164 | 461 |
| 10x / 0.5 / from 09:31 | 230 | 1,403 | 150 | 2 |
("bad" = Yahoo volume more than 5x Alpaca's for the same minute, Sep 28-Nov 20.)

## Does it drop real spikes? (Alpaca 1-min, 2022-01-15 to 2026-11-20, desks' own code, batch 7 replay)
| desk rule | trades without guard | with guard | trades that differ | mean %/trade without -> with |
|---|---|---|---|---|
| orb_vol | 807 | 806 | 1 | +0.028 -> +0.027 |
| ema_vol | 868 | 868 | 0 | −0.050 -> −0.050 |
| volspike | 1,213 | 1,213 | 3 + 3 | +0.016 -> +0.016 |
| ema_vol_v2 | 867 | 867 | 1 + 1 | −0.055 -> −0.055 |
| orb_plain / ema_plain (no volume) | 1,217 / 1,110 | same | 0 | unchanged |
| volspike_2x | 1,216 | 1,216 | 3 + 3 | +0.047 -> +0.049 |
So on clean data it changes about 1 trade in 500. LESSONS 49 (no edge in five years) is unchanged.

## (a) Re-derived paper count
- Bot bar log replay (Nov 18-25), guard off: reproduces all 16 paper trades of the 4 desks (same symbol and entry minute). Guard on: 4 change: Nov 18 ema_vol and ema_vol_v2 QQQ 12:20 (+$1.47 each) become SQQQ 14:40; Nov 19 volspike QQQ 11:04 (stop −$17.34) becomes SQQQ 11:51 (target, +4.86% in the replay); Nov 25 volspike QQQ 11:26 (+$21.16) becomes SPY 11:59.
- Archive replay (Oct 26-Nov 20), guard off: reproduces 39 of 50 paper trades (the archive is not the live feed). Of those 39, 13 lose their signal with the guard: 10 independent (Oct 27, Oct 28 volspike; Oct 29, Nov 2, 11, 12 orb_vol; Nov 4, 10, 18 ema_vol (+ v2 copies); Nov 13 volspike), net +$0.62. Adding Nov 19 from the bot log: **11 independent paper trades through Nov 20 fired on a running-volume bar**, the coach's count. The day lists differ on 4 days (mine: Nov 2 SPY and Nov 13 TQQQ; the coach's: Nov 3 and Nov 17). Nov 2 SPY is likely archive-only (the coach found SPY clean live). Oct 29 orb_vol is in both: the guard removes it although Alpaca shows a real spike in that window: when the bad bar lands on a real spike minute the guard cannot tell them apart.
- Nov 25 (today): volspike's QQQ long fired on one (the Accountant's flag is right).

## (c) Lab numbers that move
- floor-lab (Yahoo archive) desk replays: about a quarter of the volume-gated desks' trades change (Oct 1-Nov 24: orb_vol 8 of 25, ema_vol 6 of 27, volspike 11 of 39, v2 7 of 27). Plain rules unchanged. The cleaned replays are slightly less bad (orb_vol −0.40 -> −0.19, ema_vol −0.17 -> −0.10, volspike +0.09 -> +0.21 %/trade) on 22-39 trades: no verdict changes.
- Foundry batch 1 on the 1-min archive: F1/F2 identical; F3-F6 (VWAP) change 6-19 trades each, means stay within ±0.1%: all still refuted.
- Batches 2-6 that read the Yahoo 1-min archive through `load_bars` are cleaned from today on (foundry-lab re-runs them daily). None of their verdicts rested on volume.
- Batch 7 (Alpaca) is not affected.

## Comparability of paper data
From the deploy of 2026-11-25 evening, the paper desks ignore running-volume bars. Paper trades before that are kept as they are and flagged by the Accountant (BOARD item 1d); for desk verdicts, count both "all paper trades" and "trades without a running-volume signal".
