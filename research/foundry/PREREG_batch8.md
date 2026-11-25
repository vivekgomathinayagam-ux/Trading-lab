# Foundry batch 8: pre-registration (Researcher, Wed 2026-11-25 build run)

Written and committed BEFORE any of these numbers were computed. Research only; nothing here trades.

## Data
- **L5** = Alpaca 5-min SPY/QQQ, 2020-01 to latest (`data:backtests/data/alpaca5m/`). Halves: 2020-2022 and 2023-2026.
- **L1** = Alpaca 1-min SPY/QQQ, 2022-01 to 2026-11-20 (`data:backtests/data/alpaca1m/`), resampled to 5-min clock buckets. Halves: 2022-2023 and 2024-2026.
- **Y1** = Yahoo 1-min archive (`data:backtests/data/etf1m/`, Sep 28-Nov 25, volume-cleaned per LESSONS 56; the rules below use no volume), resampled to 5-min; **Y5** = Yahoo 5-min (`etf5m`). Short archives are a sanity check, not a pass condition (n too small).
- Statistic: the underlying's signed % move per trade (SPY or QQQ; long = +, short = −), decided at a 5-min close, filled at the next 5-min open, flat at the 15:55 bar's close. Costs: 0.046% round trip (foundry COST) and 2x. The paper desk version would trade TQQQ/UPRO (long) and SQQQ/SPXU (short); this tests the signal, not the ETF.
- Random control (per hypothesis cell): the same sessions, same side, a random entry bar inside the cell's entry window, same exit rule; the cell must beat the 95th percentile of 500 draws of the mean.
- Prior close = the previous session's last regular-hours close in the same file.

## H30: open-reversal ("V") days (coach, BOARD 2026-11-23; LESSONS 55)
Day definition (gap up; mirror for gap down):
- gap = 09:30 open / prior close − 1 ≥ +1.0%;
- flush: some 5-min low in 09:30-09:55 is ≤ open × (1 − 1.0%);
- V: after the flush low L, the first 5-min close between the flush bar and 10:45 with close ≥ L × 1.01. That close is T_v.
Question 1 (count): how many sessions per year, per symbol and per gap direction. No rule is built if fewer than 30 V days per gap direction in L5.
Question 2 (entries at T_v, fill next open, flat 15:55, no stop):
- **H30-with**: trade in the V's direction (gap up: long; gap down: short);
- **H30-fade**: trade against it.
Cells: with/fade x gap up/gap down = 4 cells per symbol, pooled SPY+QQQ as the decision cell (sessions where both qualify count twice; CIs are bootstrapped by day blocks). LESSONS 55 predicts both ≈ 0 (nothing left after the V).
Random control window: T_v's bar to 14:00.

## H31: impulse fade (IDEAS 2026-11-12/13 "fade after an extended leg", IDEAS impulse fade item; coach 11-24 "momentum entries deep into a swing")
Per symbol, per session, 5-min bars, entries 10:00-14:30:
- **Fade an up-impulse (short side):** leg = session high so far / lowest low before that high − 1 ≥ +1.5%. Trigger: the first 5-min bar after a bar that set the session high whose low is below the previous bar's low (first lower low), while the leg ≥ 1.5%. Short at the next open. Stop: the session high × 1.001 (checked on bar highs, filled at the stop price). Flat 15:55.
- **Fade a down-impulse (long side):** mirror (leg from the highest high before the session low ≥ 1.5% down; first higher high; stop session low × 0.999).
- One trade per side per session (the first trigger).
Cells: short side, long side; pooled SPY+QQQ is the decision cell, per-symbol reported.
Random control window: 10:00-14:30, same stop distance in % as the real trade it is paired with, same exit.

## Pass bar (any decision cell)
Pooled L5: mean net > 0 with day-block bootstrap 95% CI lower bound > 0; > 0 in both L5 halves; > 0 in L1 (both halves); > 0 at 2x costs; above the random-control p95; ≥ 60 trades in L5. A cell that passes goes to paper as a new desk key on the 3x ETFs (long side TQQQ/UPRO, short side SQQQ/SPXU), sized like the other desks.

## Standing: Newsie shadow (BOARD 2026-11-17)
All Newsie days to date (Nov 18-25, 6 sessions): sit_out = no entries; caution = skip entries inside event_risk windows (and inside a flag's stated window); bias = keep only the side Newsie favoured. Replay = the paper ledger trades of the 4 paper desks (no counterfactual entries). Shadow only until 20+ Newsie days.

## Also run here (not a hypothesis): LESSONS 56 volume guard
The running-volume guard ships as a paper bug fix (DECISIONS 2026-11-25). Its check on Alpaca (does it drop real spikes) and its effect on the paper desks are reported in `research/foundry/volguard_REPORT.md`.

## Variants counted
H30: 4 cells x 2 symbols = 8 (decision cells 4). H31: 2 sides x 2 symbols = 4 (decision cells 2). Newsie: 3 flags x 4 desks, counted in batch 6. Volume guard: 1 parameter set chosen (20x / 0.5) after looking at 6 candidates on Alpaca and Yahoo = 6 variants of a data filter (not a trading rule).
