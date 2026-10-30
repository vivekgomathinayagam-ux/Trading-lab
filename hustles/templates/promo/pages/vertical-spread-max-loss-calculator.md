# Vertical Spread Max Loss, Max Profit and Breakeven: Worked Examples (free)

Arithmetic only. Not advice, not a signal, no prediction. Options involve risk of loss, including the full premium paid or more on spreads. Prices below are made-up round numbers, per share; one contract = 100 shares. Commissions and assignment risk are not included.

## The four formulas

Let **width** = distance between the two strikes.

| Spread | Max loss | Max profit | Breakeven |
|---|---|---|---|
| Bull call (debit) | debit x 100 | (width - debit) x 100 | long strike + debit |
| Bear put (debit) | debit x 100 | (width - debit) x 100 | long strike - debit |
| Bull put (credit) | (width - credit) x 100 | credit x 100 | short strike - credit |
| Bear call (credit) | (width - credit) x 100 | credit x 100 | short strike + credit |

## Example 1: bull call spread (debit)

Buy the 100 call at 2.40, sell the 105 call at 0.90. Width 5. Net debit 1.50.

- Max loss: 1.50 x 100 = **$150** (price at or below 100 at expiry)
- Max profit: (5 - 1.50) x 100 = **$350** (price at or above 105)
- Breakeven: 100 + 1.50 = **101.50**

## Example 2: bull put spread (credit)

Sell the 100 put at 1.80, buy the 95 put at 0.60. Width 5. Net credit 1.20.

- Max profit: 1.20 x 100 = **$120** (price at or above 100)
- Max loss: (5 - 1.20) x 100 = **$380** (price at or below 95)
- Breakeven: 100 - 1.20 = **98.80**

Note the credit spread risks more than it can make here. That is normal for credit spreads, and why max loss, not credit, should set your size.

## Turn max loss into a position size

Contracts = round down( account x risk % / max loss per contract ).

| Account | Risk 5% | Example 1 ($150) | Example 2 ($380) |
|---|---|---|---|
| $1,000 | $50 | 0 | 0 |
| $5,000 | $250 | 1 | 0 |
| $10,000 | $500 | 3 | 1 |

A result of 0 means the trade is too big for your rule. Skip it or choose a narrower spread. Do not round up.

## Check yourself

1. Debit spreads: can you lose more than the debit? No.
2. Credit spreads: is max loss the credit? No, it is width minus credit.
3. Did you multiply by 100? Per-share prices become per-contract dollars.

## Want it automated?

The **Trader Toolkit** ($12, built with AI assistance) includes a risk and position-size calculator covering long options and all four vertical spread types with a risk-limit check, plus a trade journal with R-multiple stats and a trading-plan checklist pack: https://vivekgo8.gumroad.com/l/aobhdm

A free browser version of the basic calculator is in `options-position-size-calculator.html`.
