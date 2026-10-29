# How a trailing drawdown floor works (free explainer, with a worked example)

Many funded-account challenges end your account if your balance falls to a "drawdown floor". With an end-of-day trailing rule, the floor follows your best end-of-day balance up and never comes back down. Rules differ by firm: always read yours. This page is arithmetic only, not advice, and is not affiliated with any firm.

**Floor = highest end-of-day balance - max drawdown** (many firms stop the floor rising once it equals the starting balance).
**Cushion = current balance - floor.**

## Worked example (made-up numbers)
Start $50,000, max drawdown $2,000, floor stops at the starting balance.
| Day | P&L | End balance | Highest | Floor | Cushion |
|---|---|---|---|---|---|
| 1 | +420 | 50,420 | 50,420 | 48,420 | 2,000 |
| 2 | -310 | 50,110 | 50,420 | 48,420 | 1,690 |
| 3 | +880 | 50,990 | 50,990 | 48,990 | 2,000 |
| 4 | -850 | 50,140 | 50,990 | 48,990 | 1,150 |

Notice the cushion refills only when you set a new high: a winning day that does not beat your best balance does not move the floor. A static drawdown instead fixes the floor at start - max drawdown ($48,000) forever.

Want this done for you each day, including daily-loss use and a status line? I made a small workbook (built with AI assistance): [Funded Account Drawdown Tracker, coming soon to the same store](https://vivekgo8.gumroad.com/l/aobhdm). Trading involves risk of loss.
