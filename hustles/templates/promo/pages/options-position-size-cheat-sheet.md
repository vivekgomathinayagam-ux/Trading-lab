# Options Position Size Cheat Sheet (free)

How many contracts can you trade without breaking your own risk rule? This page is arithmetic only. It is not advice, not a signal, and it does not predict anything. Options trading involves risk of loss. Written with AI assistance (Claude) and checked by recalculation.

## The one formula

**Dollar risk per trade = account size x risk percent**

**Contracts = round down( dollar risk / max loss of ONE contract )**

If the answer is 0, the trade is too big for your rule. Skip it or pick a cheaper structure. Do not bend the rule.

## Max loss of one contract (x100 multiplier)

| Structure | Max loss per contract | Max profit per contract | Breakeven |
|---|---|---|---|
| Long call or put | premium paid x 100 | calls: unlimited; puts: (strike - premium) x 100 | call: strike + premium; put: strike - premium |
| Debit vertical (bull call, bear put) | net debit x 100 | (width - debit) x 100 | long strike +/- debit (call: plus, put: minus) |
| Credit vertical (bull put, bear call) | (width - credit) x 100 | credit x 100 | short strike -/+ credit (put: minus, call: plus) |

Add commissions and fees per contract to max loss if your broker charges them. Never sell naked options: their loss has no cap, so this sheet does not cover them.

## Worked examples (made-up prices)

Account $2,000, risk rule 5% per trade, so dollar risk = $100.

1. **Long option** at 0.45 ask: one contract costs $45. 100 / 45 = 2.2, so **2 contracts** (max loss $90).
2. **Debit vertical**: buy the 500 call at 2.10, sell the 501 call at 1.60. Debit 0.50 = $50 per contract. 100 / 50 = **2 contracts**. Max profit per contract (1.00 - 0.50) x 100 = $50. Breakeven 500.50.
3. **Credit vertical**: sell the 495 put at 0.70, buy the 494 put at 0.40. Credit 0.30. Max loss (1.00 - 0.30) x 100 = $70 per contract. 100 / 70 = 1.4, so **1 contract**. Breakeven 494.70.

Account $10,000, risk rule 1%, dollar risk $100. A $30-risk trade fits 3 contracts (100 / 30 = 3.3).

## Quick checks before you click

- Is max loss for the whole position at or under your dollar risk?
- Did you count fees, and are you using the ask when buying and the bid when selling (not the mid)?
- Do you also have a daily loss limit? A common idea is to stop for the day after one or two full-risk losses; pick your own number and write it down.
- Does the account fit the setup at all? Tiny accounts often fit zero contracts of a 1-point-wide SPY spread. That is information, not a reason to oversize.

## Want it done for you?

The **Options Day Trader Toolkit** is two spreadsheets: a risk and position-size calculator (long options and the four vertical spreads, with a "fits my limit" check and max contracts) and a trade journal (P&L, R-multiple, win rate, expectancy, profit factor, drawdown, streaks, calendar). $12 one time, Excel or Google Sheets, no subscription.

https://vivekgo8.gumroad.com/l/aobhdm

It is a record-keeping and arithmetic tool. It does not make anyone profitable.
