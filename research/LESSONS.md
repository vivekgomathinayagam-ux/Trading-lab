# LESSONS: what Compound City has learned (read first, every agent, every run)

This is the system's memory of what works, what doesn't, and why. Every lesson cites its evidence.
- **Who writes here:** the Session Coach (daily), the Researcher (Wed/Sat) and any interactive session.
- **How to change a lesson:** never delete one. When new evidence changes it, strike it through and add the update with a date.
- **Status tags:** `confirmed` held out of sample; `tentative` only in-sample or small n; `refuted` a tested idea that failed (kept so nobody re-tests it blindly).

## Market behaviour (SPY/QQQ intraday)
1. `confirmed` **The +5% target is almost never reachable intraday.** It hit 0 times in 89 backtest trades and 0 in 22 paper trades. Since 2010 SPY moved +5% in a day on 0.17% of days, and 3x ETFs on 3-10%. (exit study 2026-10-29; STATE)
2. `confirmed` **Flat by 15:55 beats holding overnight.** Holding gave −0.30%/trade vs +0.05%, with a worst gap of −3.4%. (research/exits/REPORT.md)
3. `tentative` **Sep 28 to Nov 2 was a down-drift regime.** Long from 09:45 to 15:55 averaged −0.13% a day on SPY/QQQ. Every trend rule's short side made money and its long side lost. That is regime, not edge: rules must be judged on both sides and on more than one regime. (foundry batch 1, 2026-11-03)
4. `confirmed` **The 0DTE GEX board does not predict the next 60-90 minutes:** no magnet, no gamma-regime range effect. (Skylit pilots 1 and 2)
5. `confirmed` **Options over-price SPY/QQQ next-day moves.** Realized moves are about 0.68-0.75x the priced 1-sigma, in both halves of 2 years. That is a lead for defined-risk premium selling, but not yet proven after bid/ask. (Skylit pilot 2)

## Our desks: why they miss moves
6. `confirmed` **The desks cannot go short SPY/QQQ directly; only the inverse ETFs give a short.**
   - Nov 2: SPY offered a 1.6% down-leg (10:28 to 15:58 ET) and all 4 trades were longs that lost.
   - Nov 3: the 5 entries were all long; none shorted the 13:30 ET breakdown.
   - Every new rule family must include a short side. (post-mortems 2026-11-02/03)
7. `confirmed` **Exits are the biggest leak.**
   - Non-CVD desks hold to 15:55 with no trailing exit, so they give back trends: Nov 3 volspike bought SPY 755.82 at 10:56 ET and the open trade was below entry by 15:00.
   - CVD exits are the opposite problem, too twitchy: Nov 3 cvd_spy held 3 minutes.
   - Fixed take-profits lost to baseline, and the ATR trail failed walk-forward. (exit study)
8. `tentative` **Entries that are already extended do worse,** as does very low ATR. Both held in both halves of the entry study, but neither passed as a filter. (research/entries/REPORT.md)

## Rule families tested (foundry batch 1, 5-min bars, 26 sessions, SPY+QQQ, costs 0.046% round trip)
9. `refuted` **Simple trend rules lose after costs:** Ripster cloud ride (F1 slow exit, F2 tight exit) and VWAP trend (F3).
   - 1-min sample (26 sessions): F2 +0.013%/trade, F3 +0.008%, F1 −0.006%. Gross edge is about +0.04-0.06%, roughly the 0.046% round-trip cost.
   - Wider 5-min sample (41 sessions, Sep 8-Nov 3): all negative. F1 −0.023% (177 trades), F2 −0.014% (243), F3 −0.023% (149).
   - Every one is negative in the first half and slightly positive in the second, which is regime drift, not edge.
   - Short sides beat long sides in both samples (the down-drift regime, lesson 3).
   - Don't re-test these as-is. Only with a new ingredient: a trend-day gate, fewer and bigger trades, or 3x-ETF execution. (foundry batch 1, 2026-11-03)
10. `refuted` **Fibonacci 50-61.8% pullback toward the session extreme (F5):**
   - It looked good on 26 sessions: 21 trades, +0.038%, 67% win.
   - It failed on 41 sessions: 49 trades, −0.050%, PF 0.64, negative in both halves.
   - The small first sample flattered it.
11. `refuted` **Fibonacci 38.2-50% pullbacks (F6) lose:** −0.061%/trade on both samples (37 and 73 trades). The 5-min CI is entirely below zero [−0.115, −0.006].
12. `refuted` **The VWAP trend-break reversal (F4) as written:** −0.015%/trade on both samples (39 and 63 trades). Its short side was positive (+0.04%) and its long side negative, which is regime again.

## Data and infrastructure
13. `confirmed` **The Yahoo real-time feed can freeze silently.** Oct 30 it froze for 74 minutes and a paper exit used the stale price. PR #2 fixes this but awaits Vivek. (research/weekly/2026-W44.md)
14. `confirmed` **Only 26 sessions of 1-minute history exist** (Sep 28 onward, Yahoo's 30-day limit), so every intraday verdict is low-power. The fix is a long-history source: Alpaca's free plan has minute bars since 2016. (2026-11-03)
15. `confirmed` **Position size makes the P&L tiny.** A $1,000 desk buys 1 SPY share, so even a perfect 0.8% SPY day pays about $6. Edge has to be proven in % terms first; dollars come from size, 3x ETFs or options, under the money rules.

## How we work (process lessons)
16. **Two samples beat one.** A rule that looks fine on 26 sessions can fail on 41 (F5). Every test runs on both archives before anyone believes it.
17. **Every session gets a post-mortem** (`research/postmortem/<day>.md` on branch `data`): what the market offered (best up and down legs), what each desk did, what it gave back, and what the foundry rules would have done. The Coach turns that into at most one lesson here per day, only when it is new.
18. **Hindsight shows opportunity; it never picks rules.** A rule changes only through a pre-registered test. Today's chart always looks obvious; the question is whether the rule works across many days.
