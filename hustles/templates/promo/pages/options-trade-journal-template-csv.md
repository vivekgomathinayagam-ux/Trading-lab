# Options Trade Journal Template (free CSV, with the formulas)

Record-keeping only. Not advice, not a signal, no prediction of results. Options involve risk of loss. Written with AI assistance (Claude). The three example rows are made up.

Download the blank-ready file: [options-trade-journal-template.csv](options-trade-journal-template.csv). It opens in Excel, Google Sheets and Numbers. Delete the three example rows and start logging.

## Columns

`date, underlying, structure, entry_price, exit_price, contracts, fees_usd, planned_max_loss_usd, net_pnl_usd, r_multiple, followed_plan, note`

## The two formulas (put them in the sheet)

- Long options and debit spreads: `net_pnl_usd = (exit_price - entry_price) * 100 * contracts - fees_usd`
- Credit spreads (entry is the credit, exit is the debit paid to close): `net_pnl_usd = (entry_price - exit_price) * 100 * contracts - fees_usd`
- `r_multiple = net_pnl_usd / planned_max_loss_usd`

## Check against the example rows

| Row | Calculation | Net P&L | R |
|---|---|---|---|
| SPY 570C, 2 contracts (max loss $120) | (1.80 - 1.20) x 100 x 2 - 1.30 | +118.70 | +0.99 |
| QQQ put debit spread (max loss $150) | (0.70 - 1.50) x 100 x 1 - 1.30 | -81.30 | -0.54 |
| SPY call credit spread (max loss $100) | (1.00 - 0.00) x 100 x 1 - 1.30 | +98.70 | +0.99 |

(R = net P&L / planned max loss; the CSV stores the same numbers.)

## After 30 trades

Sort by `followed_plan`, then compare average R when you followed the plan against when you did not. That one split is usually more informative than the total.

## Want the stats done for you?

The Trader Toolkit ($12, Gumroad) is a ready-made journal workbook with R-multiple stats, drawdown, streaks and a calendar view, plus an options risk and position-size calculator: https://vivekgo8.gumroad.com/l/aobhdm . Built with AI assistance; no results claims.
