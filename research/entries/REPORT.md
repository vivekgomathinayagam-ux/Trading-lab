# Entry-quality study: report (2026-10-29)

Brief: Vivek, 2026-10-29. Pre-registration: `PREREG.md` (written before any result). Code: `lab/floor/entry_lab.py` (dataset) and `lab/floor/entry_analysis.py` (analysis). Data: `signals.csv.gz` (1,094 signals × 28 features + outcomes) and `analysis.json` (every number below). **No production desk, entry signal, risk cap or sizing was changed.**

## Bottom line
1. **No experimental entry configuration beat the original desks out-of-sample in a way that is statistically meaningful.** None of the 90 filter × desk configurations passed the pre-registered bar (better on train AND validation, with at least 5 trades in each). So nothing went to the final test comparison.
2. **Why the desks underperform:** the average signal loses money after costs in every rule. Signals tend to fire after price is already extended. Low-volatility conditions give moves too small to cover costs.
3. **Two findings held in both halves of the data** (train Oct 1-15 and held-out Oct 16-29):
   - **Extension hurts.** Signals that fire when price is already far above the day's open lost more.
   - **Low volatility hurts.** Signals in the lowest-ATR third lost the most.
   Both are worth a forward shadow test. Neither is proven.
4. **cvd_tqqq:** its result comes from its **first signal of the day** (+0.46%/trade). Later CVD turns lose (about -0.07%). Post hoc, the first signal beat a plain 10:00 AM TQQQ entry with the same exit by +0.40%/trade (18 of 21 days). This was not pre-registered, so treat it as a lead, not proof.
5. **Bug found (paper only, harmless so far):** `CVDTurn.signal()` does not check the symbol. A CVD desk could buy the wrong ETF in one edge case. I did not change it, because the desk rules are frozen and it needs your yes. Details below.

**The sample is the limit.** 21 tradeable sessions. Desk-level validation and test periods hold only 1-5 trades per desk. Signal-level analysis (1,094 signals) is the only place with any statistical power, and signals on the same day are correlated. All intervals below therefore resample whole days.

## How it was done
- Every signal each production rule fired from Oct 1-29, not just the one trade per day a desk takes. Engine order replayed exactly. Rules: orb_vol, ema_vol, ema_vol_v2, volspike, cvd_spy, cvd_tqqq. GEX has no rule yet, so nothing to test.
- **Check:** taking the first signal of each day reproduces all **109 real desk trades** (entry time and return).
- **Entry and costs:** each signal enters at the next bar's open. Outcome = the desk's own exit (stop -2.5%, target +5%, 15:55 flat, CVD exit for CVD rules), net of engine slippage both sides plus a 0.003% sell fee. Also tested at 2x slippage.
- **Features:** 28, computed at the signal bar's close from that bar and earlier only, in 10 groups (volume, CVD, VWAP, EMA 9/20, trend, volatility, support/resistance, time, market, breakout). Price distances are in ATR units so 1x and 3x ETFs compare.
- **Splits, fixed in advance:**
  - train Oct 1-15 (11 sessions)
  - validation Oct 16-22 (5)
  - test Oct 23-29 (5)
  - plus an expanding walk-forward for the score.

## Phase 1: what relates to better outcomes
Spearman correlation of each feature with the trade outcome. Pooled across rules (each rule ranked on its own), 90% day-block intervals.

| feature | train ρ [90%] | held-out ρ [90%] | read |
|---|---|---|---|
| distance above day's open (ATR) | -0.11 [-0.26, -0.02] | -0.17 [-0.35, -0.00] | **holds**: more extended = worse |
| distance above opening-range high (ATR) | -0.14 [-0.32, -0.02] | -0.15 [-0.32, -0.01] | **holds**: same idea |
| ATR % of price (volatility) | +0.12 [-0.00, +0.26] | +0.10 [+0.05, +0.17] | holds (borderline on train); also strongly tied to bigger MFE (+0.31 / +0.25) |
| 5-day return | -0.24 | **+0.24** | **flips sign**: regime-dependent, unusable |
| prior-day return | -0.12 | **+0.27** | **flips sign** |
| distance above prior-day high | -0.21 | +0.13 | flips |
| cumulative relative volume | +0.09 | -0.09 | flips |
| CVD slope / acceleration, EMA alignment, VWAP, 30-min trend, time of day, breakout strength, close location | all \|ρ\| < 0.07 on train | | no usable relationship |

**Extension, in plain numbers** (cut points from train, applied to both halves):

| | lowest third | highest third |
|---|---|---|
| distance above open: train | +0.02% per signal | -0.09% [-0.20, -0.00] |
| distance above open: held-out | -0.04% | **-0.15% [-0.24, -0.08]** |
| ATR %: train | **-0.11% [-0.15, -0.08]** | +0.01% |
| ATR %: held-out | **-0.17% [-0.34, -0.07]** | -0.05% |

**Per rule,** only two relationships held in both halves with intervals clear of zero:
- volspike vs distance above open: train -0.28, held-out -0.24.
- ema_vol_v2 vs EMA alignment: +0.16 / +0.08, which is small.

28 features × 7 groups is 196 tests, so about one "hold" is expected by chance. The extension finding is more credible than that because the two different measures of it agree.

## Phase 2: regimes
Labels are causal at signal time, from the instrument's index, signed for inverse ETFs. Mean outcome per signal, with train / held-out in brackets.
- **volspike:**
  - high-volatility days: +0.08% (PF 1.24; train +0.01%, held-out +0.40%; 8 days in all)
  - low and normal volatility: -0.15% and -0.20%, negative in both halves
- **cvd_tqqq:**
  - strong bull trend: **-0.18%** (PF 0.22), negative in both halves (-0.10 / -0.28)
  - sideways and strong-bear (a dip for TQQQ): slightly positive (+0.06 / +0.02)
- **orb_vol:** negative in every regime with data. Breakout days were worst (-0.36%, PF 0.21).
- **ema_vol / v2:** too few signals per regime (5-34) to say anything.
- **cvd_spy:** between -0.02% and -0.05% in every regime. Nothing separates.

No strategy is reliably positive in any regime cell with enough days. These are descriptions, not rules.

## Phase 3: entry-quality score (shadow only, not a probability)
- **How it was built:** fit on train only, as the sign-weighted rank-sum of the 12 features with |train ρ| ≥ 0.05.

| | low third | mid | high third | score ρ |
|---|---|---|---|---|
| train (in-sample) | -0.15% | -0.08% | **+0.04%** | 0.23 |
| validation | -0.16% | -0.01% | -0.04% | 0.11 |
| test | -0.15% | -0.09% | -0.12% | 0.12 |
| walk-forward (refit daily) | -0.15% [-0.24, -0.09] | -0.05% | -0.08% [-0.16, -0.00] | |

- **Out-of-sample:** the score separates bad from less-bad. The bottom third is reliably worst, but even the top third loses money. MFE is a bit larger in the top third; MAE is about the same.
- **Ablation on validation:** no single feature carries the score. Dropping the prior-day-high, opening-range or open-distance features *raised* the validation spread. The score's makeup is unstable, which is typical of overfitting.
- **Verdict:** not usable as a filter. It could be logged in shadow to keep testing.

## Phase 4: filters and combinations
Fifteen filters and combos were tested on every desk (90 configurations): rvol>1, CVD slope>0, above VWAP, EMA aligned, market confirm, 30-min trend>0, range ratio≥1, before 11:30, breakout above train median, CVD+rvol, CVD+VWAP, EMA align+market, ORB+rvol, range ratio+volume expansion, and score top third. Each filtered desk takes the first qualifying signal of the day.
- **Candidates passing the pre-registered bar: none.** The validation week had only 1-5 trades per desk, so the "≥5 trades in train and validation" bar was rarely even reachable.
- **Some filters look good on one period and bad on the next.** Examples:
  - ema_vol + rvol>1: +0.18% in validation, -0.90% in test.
  - orb_vol + breakout strength: +0.56% train, -0.61% validation, -0.40% test.
  That is the overfitting pattern the rules guard against.
- **Signal level** (more data, but post hoc): the clearest improvement is cvd_tqqq before 11:30 (validation +0.18%, test +0.38% [+0.17, +0.61] vs -0.06% to -0.14% after). But it was flat on train (-0.02%), and it overlaps with the first-signal effect below.

## Phase 5: forward comparison
- **No candidates, so no experimental desk was compared on test.** Re-testing filters on test after seeing them would break the rules of the study.
- **Original desks, desk level:**

| desk | train | validation | test |
|---|---|---|---|
| orb_vol | 10 trades, -0.30%/trade | 1, -0.32% | 4, -0.21% |
| ema_vol | 7, +0.08% | 4, -0.44% | 5, -0.49% |
| ema_vol_v2 | 7, +0.11% | 4, +0.10% | 4, -0.58% |
| volspike | 11, -0.15% | 5, +0.76% | 5, +0.30% |
| cvd_spy | 11, -0.06% | 5, -0.00% | 5, +0.09% |
| cvd_tqqq | 11, +0.13% | 5, +0.94% | 5, +0.69% |

- **Average signal across all rules:** -0.06% (train), -0.06% (validation), -0.12% (test). At 2x slippage: -0.14%, -0.14%, -0.20%.

## Why cvd_tqqq works, and why that matters
- **First signal vs later signals:** first signal +0.46%/trade [+0.24, +0.70] over 21 days, all three periods positive (+0.13, +0.94, +0.69). Every later CVD turn on TQQQ: -0.07% on average.
- **Typical timing:** the first signal comes 17-86 minutes after the open, median about 10:02 AM.
- **Fixed-time control (post hoc):** a plain TQQQ entry at fixed times, with the same exits:

| entry time | 9:50 | 10:00 | 10:15 | 10:30 | 11:00 | 1:00 PM |
|---|---|---|---|---|---|---|
| return per trade | +0.18% | +0.05% | +0.16% | +0.02% | -0.33% | -0.22% |

- **Result:** the first CVD signal beat the 10:00 entry on 18 of 21 days, by +0.40% [+0.22, +0.61]. So the signal seems to add something beyond "be long TQQQ in the morning".
- **Caveats:** one month, Nasdaq mornings drifting up, chosen after looking. The one-entry-per-day rule already makes the desk trade only the first signal, so no change is needed. What it tells us is where to look: the morning reversal, not CVD turns in general.

## Bug: `CVDTurn.signal()` does not check the symbol
- **The flaw:** `signal()` compares only the bar time. The bot handles symbols in a fixed order within each minute. If TQQQ's signal bar is skipped as stale but a fresh UPRO, SQQQ or SPXU bar arrives for that same minute, `cvd_tqqq` could buy that ETF instead. Yahoo drops 1-6% of UPRO/SPXU minutes, so the timing mismatch can happen.
- **Impact so far:** no wrong-symbol trade in the paper ledger. Paper only.
- **Fix:** a one-line check that the bar's symbol is the rule's own (`signal()` needs the symbol). It touches a frozen desk's code, so it waits for your yes.

## What I recommend (nothing implemented)
1. **Keep the Month-1 desks exactly as they are.** Nothing here justifies an entry change.
2. **Shadow logging (your yes needed, logging only, no blocking):** have the bot record, for every signal, distance above open (ATR), distance above OR high (ATR), ATR % and the frozen score. After about 20 more sessions, test the two pre-registered hypotheses on brand-new days:
   - **H1:** skip signals in the top third of distance-above-open.
   - **H2:** skip signals in the bottom third of ATR %.
3. **Fix the CVD symbol bug** (your yes needed).
4. **Re-run this study** at about 40 sessions (mid-November) with the same code and splits rolled forward. Only filters that survive new data move to a separate paper desk.
5. **For the Researcher:** the cvd_tqqq morning effect is the most interesting lead. ORB and EMA show no sign of a fix through filters; their verdict comes with the Month-1 report.

## Count
- Correlations: 196 feature tests plus 4 secondary outcomes.
- Regime cells: 3 dimensions.
- Score: 1, plus 12 ablations.
- Filters: 90 configurations.
- Post-hoc checks: 3 (extension thirds, cvd_tqqq first/AM, fixed-time control).
- Logged in `research/VARIANTS.md` as 94 configurations (the 90 filters, the score, and the 3 post-hoc checks); running total 129.
