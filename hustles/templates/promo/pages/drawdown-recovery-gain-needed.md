# Drawdown Recovery: How Much Gain You Need to Get Back to Even (free table)

Arithmetic only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude).

## The formula

If you lose a fraction `d` of your account, the gain needed to get back to the starting balance is:

**Required gain = d / (1 - d)** (equivalently 1 / (1 - d) - 1)

Losses and gains are not symmetric: a 50% loss needs a 100% gain.

## Table on a $1,000 account (computed by script)

| Drawdown | Dollars lost | Balance left | Gain needed to recover | Dollars to regain |
|---|---|---|---|---|
| 5% | 50 | 950 | 5.3% | 53 |
| 10% | 100 | 900 | 11.1% | 111 |
| 15% | 150 | 850 | 17.6% | 176 |
| 20% | 200 | 800 | 25.0% | 250 |
| 25% | 250 | 750 | 33.3% | 333 |
| 30% | 300 | 700 | 42.9% | 429 |
| 40% | 400 | 600 | 66.7% | 667 |
| 50% | 500 | 500 | 100.0% | 1,000 |
| 60% | 600 | 400 | 150.0% | 1,500 |
| 75% | 750 | 250 | 300.0% | 3,000 |

Check: 20% down leaves $800; $800 x 1.25 = $1,000, so +25% is needed. 50% down leaves $500; $500 x 2 = $1,000, so +100%.

## Losing streaks at a fixed risk per trade

If each loser costs a fixed percent of the *current* balance, n losses in a row leave `(1 - r)^n` of the account.

**Risk 2% per trade**

| Losses in a row | Account down | Gain needed to recover |
|---|---|---|
| 3 | 5.9% | 6.2% |
| 5 | 9.6% | 10.6% |
| 8 | 14.9% | 17.5% |
| 10 | 18.3% | 22.4% |
| 15 | 26.1% | 35.4% |
| 20 | 33.2% | 49.8% |

**Risk 5% per trade**

| Losses in a row | Account down | Gain needed to recover |
|---|---|---|
| 3 | 14.3% | 16.6% |
| 5 | 22.6% | 29.2% |
| 8 | 33.7% | 50.7% |
| 10 | 40.1% | 67.0% |
| 15 | 53.7% | 115.8% |
| 20 | 64.2% | 179.0% |

Check: 10 losses at 2% leave 0.98^10 = 0.8171, so down 18.3%, needing +22.4%.

## Reading it honestly

- Smaller risk per trade keeps a bad streak shallow, which keeps the hole easy to climb out of. This is arithmetic, not a promise about any strategy.
- Streaks of this length are possible even for strategies that win more than they lose.
- Fees add to every loss, so the real hole is slightly deeper.
- Many funded-account and personal rules set a daily or total loss limit for exactly this reason.

## Track your own drawdown

The **Trader Toolkit** ($12, built with AI assistance) has a journal that tracks your running equity, drawdown and streaks from your own trades, plus a position-size calculator that checks a trade's max loss against your risk limit: https://vivekgo8.gumroad.com/l/aobhdm

Related free pages: risk-of-ruin table, daily loss limit and pre-trade checklist, small-account position sizing.
