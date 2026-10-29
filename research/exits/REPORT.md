# Exit study report (2026-10-29)

Question: are our exits closing winners too early? Scope: exits only; entries, indicators and desk rules untouched. Pre-registered in `PREREG.md`. Code: `lab/floor/exit_lab.py` (tests: `lab/tests/test_exit_lab.py`). Full tables: `TABLES.md`. Per-trade data: `trades_mfe.csv`, `results.json`.

**Sample:** 89 trades from the 5 desks (14-20 each) over 20 sessions, Oct 1-28. That is small. Every number below carries wide error bars. **18 exit variants x 5 desks were compared, so a few "wins" are expected by chance.**

## Verdict
**No exit change is supported yet. Nothing was changed.** Fixed take-profits made results worse. ATR trailing stops looked best in the sample, but they did not hold up walk-forward. The two exits that look worth a forward paper test are the ATR trail on the CVD desks, as separate clone desks.

## 1. Audit of the current exits
- **What +0.2% is:** the move of the traded ETF's own price, entry to exit, after slippage. It is not the index. ETFs like TQQQ/UPRO already carry 3x leverage inside that price, and SQQQ/SPXU are inverse.
- **Instrument vs position:** the same number. Each desk buys whole shares with almost the whole $1,000 book (SPY/QQQ: 1 share = 72-77% of the book), so move % is about equal to P&L % of the book.
- **The +5% target** is a real take-profit on that ETF price. It is checked on every 1-minute high and fills at +5% (or the open if it gaps through). It has fired **0 times in 89 trades**. Only 1 trade (1%) even touched +5% before its stop.
- **How trades actually ended:** 47 at the 3:55 PM flat (53%), 40 on the CVD sell turn (45%), 2 stopped out (2%), 0 at target.
- **Why CVD exits happen when they do:** the sell turn is detected when a 3-minute candle closes with CVD falling from its 5-candle high. The order fills at the next bar's open. The two CVD desks hold about 15-20 minutes on average, which is why their wins are small.
- **Replay check:** my replay reproduces all 89 baseline exits (price and reason) from the real engine.

## 2. What was available (max favorable excursion)
| | all desks | cvd_tqqq | volspike | orb_vol |
|---|---|---|---|---|
| median best price after entry (to 3:55) | +0.48% | +1.61% | +0.67% | +0.20% |
| reached +1% before the -2.5% stop | 25% | 65% | 30% | 7% |
| reached +2% | 12% | 30% | 20% | 7% |
| reached +5% | 1% | 5% | 0% | 0% |
| mean give-back from peak to the 3:55 close | 0.85 pts | 1.70 | 0.75 | 0.73 |
| median minutes to reach +1% (when reached) | 38 | 25 | 78 | 69 |

- **Big moves are rare.** Three of five desks (ORB, EMA, CVD-SPY) almost never saw +1%.
- **Holding to the close does not pay more:** average hold-to-close return was +0.04% vs +0.06% for the current exits.
- **CVD exits, 40 trades:** after the sell, price rose another 0.5%+ within an hour in only 12 (30%). It was higher at 3:55 in 22 of 40, but the average change from the exit price to the close was -0.17%. So CVD is not systematically selling right before rallies. It is mixed.

## 3. Exit alternatives (pooled over desks, 1x costs; baseline = +0.064%/trade, PF 1.27, max DD -11.5%)
| exit | expectancy | PF | max DD | avg hold | vs baseline (90% interval) |
|---|---|---|---|---|---|
| Fixed take-profit +0.5% | -0.02 | 0.93 | -8.1% | 179 min | -0.08 [-0.22, +0.05] |
| +1% | -0.06 | 0.83 | -12.2% | 243 | -0.12 [-0.29, +0.02] |
| +1.5% / +2% / +3% | +0.02 / 0.00 / +0.05 | 1.05 / 1.00 / 1.13 | -11% | 255-281 | all negative, intervals include 0 |
| Trail 0.5% / 1% / 1.5% | +0.03 / +0.07 / +0.06 | 1.17 / 1.29 / 1.19 | -6.5% / -9.8% / -9.8% | 120 / 210 / 252 | about 0 |
| **ATR trail k=2** | **+0.115** | **1.55** | **-7.0%** | 59 | +0.05 [-0.06, +0.17] |
| ATR trail k=3 | +0.10 | 1.38 | -8.5% | 115 | +0.04 [-0.10, +0.18] |
| Half off at +1% / +2% | +0.03 / +0.06 | 1.12 / 1.25 | -11.9% | 161 | -0.04 / -0.01 |
| Half at +1.5%, trail 1% | +0.04 | 1.16 | -11.2% | 154 | -0.03 |

(CVD-only exits are in section 4. Every interval includes zero except half-off at +1%, which is slightly negative.)

**Why fixed take-profits lose:** they cut winners to a fixed small size while losers still run to the -2.5% stop or the close. Win rate rises (64% at +0.5%) but average win shrinks to 0.39% against an average loss of 0.74%.

## 4. Per desk
| desk | baseline expectancy (PF, max DD) | best in-sample alternative | out-of-sample (walk-forward, same trades): picked vs baseline | read |
|---|---|---|---|---|
| ORB + volume (14 trades) | -0.29% (0.43, -4.0%) | ATR k=2: -0.25% | -0.55% vs -0.12% | Entries are the problem (36% win rate, median best price +0.2%). No exit fixes it. |
| EMA 9/21 + volume (15) | -0.21% (0.33, -3.9%) | ATR k=2: -0.07% | -0.32% vs -0.37% | Every tighter exit loses less, but all stay negative. Same: entries. |
| Volume spike (20) | +0.19% (1.58, -4.9%) | Trail 1.5%: +0.23% | +0.10% vs +0.52% | Baseline is already about the best. Keep. |
| CVD SPY (20) | -0.01% (0.86, -0.9%) | ATR k=3: +0.09% (PF 1.86, DD -0.7%); delay 2-3 candles: +0.03% | +0.02% vs +0.01% | Small gain with a lower interval above 0, but tiny in dollars and no out-of-sample gain. Forward test. |
| CVD TQQQ (20) | +0.46% (PF 10.2, DD -0.9%) | ATR k=2: +0.63% (PF 3.2, DD -2.5%); trail 1%: +0.56% | +0.31% vs +0.55% | Looks better in-sample, but with 3x the drawdown, and the out-of-sample result is worse. Forward test as a clone. |

**The CVD exit is what keeps CVD losses small.** On cvd_tqqq, removing it (fixed targets only) cut expectancy from +0.46% to +0.32% and pushed the average loss from -0.13% to -1.7%. On the sample, its early exits look like risk control, not lost profit.

## 5. Out-of-sample and controls
- **Walk-forward (pooled):** picking the best exit on earlier days each time and applying it the next day gave **+0.06%/trade vs +0.19% for just keeping the baseline**, on the same 52 later trades. The pick flipped between fixed targets, trails and baseline almost every few days, a sign the in-sample ranking is mostly noise. Per desk, the pick beat baseline on 2 of 5 desks (EMA, CVD SPY, both by tiny margins).
- **Random-entry control (3,600 entries):** every price exit loses about 0.07-0.13% per trade on random entries, which is roughly the cost of slippage. So Oct 2026 had no drift to exploit, and exits only reshape risk; they don't create edge. Our signals added about +0.15% per trade on top of random with the baseline exit, with a thin sample.
- **Cost stress:** at 2x slippage baseline is -0.01% and ATR k=2 is +0.04%. At 3x all exits are negative (baseline -0.10%, ATR k=2 -0.04%).

## 6. Is the 3:55 PM forced close limiting profit?
No, not in this sample. For the 44 trades that were flattened at 3:55 and had a next session, holding them to the next day's 3:55 (same -2.5% stop, +5% target from entry) averaged **-0.30% vs +0.05%** flat. It triggered 8 stops, the worst overnight gap was -3.4%, and the worst trade ended -5.0%. Leveraged ETFs gap hard. Overnight holding is a separate swing-strategy question that needs its own test.

## 7. What I recommend (nothing implemented)
1. Keep all five desks' exits as they are for the Month-1 test (frozen rules). They are not the weak point; ORB and EMA entries are.
2. Add two **clone desks** in paper, sharing the original desks' entries: `cvd_tqqq_atr2` and `cvd_spy_atr3` (ATR trail instead of the CVD exit). Judge them forward only, against their parents. That brings the paper count to 8 of 8.
3. Re-run this study when the archive holds about 40 sessions (mid-November), and once more on the Month-1 paper trades. A real exit improvement should show up again on new days.
4. Park partial exits, fixed take-profits, and overnight holding. They did not help here.

## Limits (read these)
- 20 sessions in one regime (a month with Nasdaq mornings drifting up). Per-desk samples are 14-20 trades. Nothing here is a statistically firm win.
- ATR here is a 14-period average of 5-minute true ranges, carried across sessions. It is one reasonable definition; other lookbacks were not tried (and would add to the variant count).
- Returns are per-trade on the position at full exposure; real fills use whole shares, so SPY/QQQ (1 share) can't split a position for partial exits.
- A trailing exit that is checked on 1-minute bars can still be gapped through on the next bar; the fills use min(open, level), which is the realistic side.
