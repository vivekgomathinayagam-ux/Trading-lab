# Long Option Contracts From a Stop Percentage: How Many Can You Buy? (free table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss, and you can lose your whole premium. Premiums, stops and account sizes below are made-up round numbers. Written with AI assistance (Claude); every cell recomputed by script.

## The rule

**Max loss per contract = premium x 100 x stop %** (a 100% stop means you accept losing the whole premium)

**Contracts = round down( account x risk % / max loss per contract )**

A result of **0 means the position does not fit your rule**. Choose a cheaper contract or skip it. Do not bend the rule. A stop is an intention, not a guarantee: a fast market or a gap can fill you worse, so a 100% stop (full premium at risk) is the only version where max loss is known in advance.

## $1,000 account, 5% risk ($50 per trade)

| Premium (cost of 1 contract) | 25% stop | 50% stop | 100% stop |
|---|---|---|---|
| $0.50 ($50) | 4 | 2 | 1 |
| $1.00 ($100) | 2 | 1 | 0 |
| $2.00 ($200) | 1 | 0 | 0 |
| $3.00 ($300) | 0 | 0 | 0 |
| $5.00 ($500) | 0 | 0 | 0 |

## $2,000 account, 2% risk ($40 per trade)

| Premium (cost of 1 contract) | 25% stop | 50% stop | 100% stop |
|---|---|---|---|
| $0.50 ($50) | 3 | 1 | 0 |
| $1.00 ($100) | 1 | 0 | 0 |
| $2.00 ($200) | 0 | 0 | 0 |
| $3.00 ($300) | 0 | 0 | 0 |
| $5.00 ($500) | 0 | 0 | 0 |

## $5,000 account, 2% risk ($100 per trade)

| Premium (cost of 1 contract) | 25% stop | 50% stop | 100% stop |
|---|---|---|---|
| $0.50 ($50) | 8 | 4 | 2 |
| $1.00 ($100) | 4 | 2 | 1 |
| $2.00 ($200) | 2 | 1 | 0 |
| $3.00 ($300) | 1 | 0 | 0 |
| $5.00 ($500) | 0 | 0 | 0 |

## $10,000 account, 1% risk ($100 per trade)

| Premium (cost of 1 contract) | 25% stop | 50% stop | 100% stop |
|---|---|---|---|
| $0.50 ($50) | 8 | 4 | 2 |
| $1.00 ($100) | 4 | 2 | 1 |
| $2.00 ($200) | 2 | 1 | 0 |
| $3.00 ($300) | 1 | 0 | 0 |
| $5.00 ($500) | 0 | 0 | 0 |

## What the tables show

- Tighter stops let more contracts fit, but tight stops on option premiums are hit by ordinary noise more often. The table sizes a loss; it says nothing about how often you will take it.
- On a $1,000 account with a 5% rule, a $2.00 contract needs a stop of 25% or tighter just to fit once; a 100% stop leaves it at 0.
- Add commissions to max loss before rounding down (see the break-even-with-fees page).
- Selling options naked has no capped loss, so no table can size it.

## Want it ready-made?

The **Trader Toolkit** ($12, built with AI assistance) has a risk and position-size calculator with a risk-limit check, a journal with R stats, and a trading-plan checklist pack: https://vivekgo8.gumroad.com/l/aobhdm
