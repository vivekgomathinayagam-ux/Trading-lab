# Exit study: pre-registration (written 2026-10-29, before any exit result was computed)

Question (Vivek): are our exits closing winners too early? Entries and indicators are NOT touched.

## Frozen
- Entries: exactly the entries the shared core makes (`strategies/daytrade/core.py`), found by one replay of the 23-session 1-minute archive (3 warm-up sessions, 20 traded). Desks: orb_vol, ema_vol, volspike, cvd_spy, cvd_tqqq. (GEX: no entries exist, nothing to test.) One entry per desk per day, so exit choice cannot change which trade is taken.
- Costs: the engine's slippage per side (0.02% 1x ETFs, 0.05% 3x), plus 0.003% regulatory fee on sells, $0 commission. Stress at 2x and 3x slippage.
- Intrabar order: stop first, then target (engine rule). Trailing levels use the high-water mark through the PRIOR bar only, so a bar's own high never lifts the stop it then tests.
- Hard stop -2.5% stays in every variant. Flat at 15:55 stays in every variant.
- Returns are per trade on the position (full-book exposure, no share rounding), so partial exits are measurable.

## Variants (20, all counted)
- Baseline = stop -2.5%, target +5%, 15:55 flat, plus the CVD sell exit on the two CVD desks.
- A fixed take-profit (CVD exit OFF on the CVD desks): +0.5, 1, 1.5, 2, 3, 5%  [6]
- B trailing from entry: 0.5%, 1%, 1.5% below the high-water mark; ATR trail (14 x 5-min ATR, k = 2 and 3)  [5]
- C partial: 50% at +1% / 50% at +2% (rest keeps the baseline exits); 50% at +1.5% then 1% trail on the rest  [3]
- D CVD desks only: delay the sell exit 1, 2, 3 candles (3/6/9 min); confirmation (exit when a candle closes below the sell candle's low, else at 5 candles)  [4]
- Reference rows: "baseline without CVD exit" (stop/5%/15:55) [1, shares A's 5% row]
Total tried: 18 distinct variants + baseline + CVD-off reference.

## How results are judged
1. MFE/MAE per trade (entry to 15:55) to see what was available.
2. Per desk and pooled: expectancy, win rate, avg win/loss, profit factor, drawdown, total return, hold time, % reaching each target.
3. Out-of-sample: chronological walk-forward. From day 9 on, choose the variant with the best expectancy on EARLIER trades only (per desk, and pooled across desks), apply it to the next day. Compare with baseline on the same days.
4. Paired bootstrap (resample days) of variant minus baseline, 90% interval.
5. Random-entry control: ~3,600 random long entries (same 6 ETFs, same days, 09:35-15:30) through every price-based exit. If an exit "wins" equally on random entries it is exploiting the month's drift, not helping our signals.
6. Verdict labels: PROMISING (beats baseline out-of-sample AND interval above 0 AND not explained by the random control), INCONCLUSIVE, WORSE. With <=20 trades per desk, expect INCONCLUSIVE for most; nothing is adopted from this alone.

## Not allowed
No permanent change to the frozen month-1 desks. Any adoption = a new paper desk clone with the new exit, judged forward.
