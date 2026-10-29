# Entry-quality study: pre-registration (2026-10-29, written before any result)

Brief from Vivek (2026-10-29): improve the QUALITY of entries. Research only. No production desk, entry signal, risk cap or sizing changes. Everything experimental stays separate.

## Data and units
- Yahoo 1-minute archive (branch `data`, `backtests/data/etf1m/`), Sep 28 - Oct 29 2026: 24 sessions, 3 warm-up, **21 tradeable**.
- **Unit of analysis = every signal fire**, not only the one trade a desk takes per day. A signal = the rule's own `signal()` returning true on a bar inside the entry window (09:35-15:30). Rules: orb_vol, ema_vol, ema_vol_v2, volspike, cvd_spy, cvd_tqqq (fresh instances of the production classes; nothing modified).
- Signals on the same day are correlated, so all intervals resample whole DAYS (block bootstrap).
- Entry for every signal = next bar open of that symbol plus engine slippage (0.02% 1x, 0.05% 3x per side), as the engine does.

## Outcomes
- **Primary:** net return of the desk's own exit from that entry (stop -2.5%, target +5%, 15:55 flat, CVD sell exit for CVD rules), net of slippage both sides and a 0.003% sell fee.
- Secondary: net forward return at 30 and 60 minutes; MFE and MAE to 60 minutes and to 15:55.

## Features at the signal bar's close (causal; only that bar and earlier)
Price distances are in units of the symbol's 5-minute ATR (14 candles) so 1x and 3x ETFs compare.
1. Volume: bar volume / median of prior 20 bars; / same-minute 5-day mean; cumulative day volume / prior-5-day mean to the same minute (rvol); last-5-bar volume expansion.
2. CVD (1-minute close-location delta, session cumulative): 15-bar and 5-bar slope (net delta / volume), acceleration (slope5 now minus 5 bars ago), session CVD / session volume.
3. VWAP: (close - VWAP) / ATR.
4. EMA 9/20 on 5-minute clock candles: alignment (+1 close>EMA9>EMA20, -1 reverse, 0 mixed), spread / ATR.
5. Trend: 30-minute change / ATR; change since open / ATR; prior-day return and 5-day return (divided by leverage).
6. Volatility: ATR % of price / leverage; range so far / prior-5-day range to the same minute.
7. Support/resistance: distance below the day's high / ATR; above prior-day high / ATR; above opening-range (15m) high / ATR; count of OR-high crosses today.
8. Time: minutes since 09:30.
9. Market: the instrument's index (QQQ for QQQ/TQQQ/SQQQ, SPY for SPY/UPRO/SPXU), signed for inverse ETFs: return since open and 30-minute return; the other index's return since open, signed the same way.
10. Breakout: (close - prior 15-bar high) / ATR; close location in the bar; number of earlier same-rule signals on that symbol today.

## Splits (chronological, fixed now)
- **Train:** Oct 1-15 (11 sessions). All discovery, thresholds, weights and choices use train only.
- **Validation:** Oct 16-22 (5 sessions). Used once to accept or reject candidates from train.
- **Test:** Oct 23-29 (5 sessions). Looked at once, at the end, for the final comparison. No choice may be revisited after seeing test.
- Plus an expanding walk-forward for the score (refit before each day from Oct 16 on, using earlier days only).

## Phase plan
1. Feature vs outcome: Spearman rank correlation per rule and pooled, on train, with day-block 90% intervals; then the same on validation+test to see if the sign holds.
2. Regimes, labelled causally at signal time from the instrument's index: trend (strong bull / strong bear / sideways / mild), volatility (high / normal / low by range ratio), structure (breakout at day high / reversal against the morning direction / neither). Strategy x regime table.
3. Score (shadow only): pooled, sign-weighted rank-sum. Features ranked within each rule on train; a feature enters with weight sign(train rho) only if |pooled train rho| >= 0.05; equal weights. Judged by score terciles (cut points from train) on validation and test: expectancy, PF, MFE, MAE. Not a probability.
4. Filters, fixed list: rvol>1; CVD 15-bar slope>0; above VWAP; EMA aligned (+1); market confirm (signed index since open >0); 30-min trend>0; range ratio>=1; before 11:30; breakout strength above train median; score top tercile. Combos: CVD+rvol, CVD+VWAP, EMA align+market, ORB+rvol, range ratio+volume expansion. Each filtered desk takes the first QUALIFYING signal of the day (desk emulation, checked against the real engine). A filter is a candidate only if it beats the unfiltered desk on train AND validation with >= 5 trades in each. Ablation: drop each score feature, refit on train, compare validation.
5. Final: original vs candidates on test, 1x and 2x slippage; trades, return, expectancy, win rate, PF, max DD, avg win/loss, MFE/MAE, frequency, by regime.

## Honesty rules
- Count every feature, filter and combo in `research/VARIANTS.md`.
- With 21 sessions and many comparisons, some will look good by chance. A result counts as PROMISING only if it is positive on train, validation AND test with intervals that do not cross zero on the held-out days; otherwise INCONCLUSIVE or REJECTED.
- Nothing is wired into a desk from this study. A survivor becomes a separate shadow log, then (with Vivek's yes) a separate paper desk.
