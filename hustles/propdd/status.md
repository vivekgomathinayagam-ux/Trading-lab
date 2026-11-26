# Funded-Account Drawdown Tracker: status
**Stage:** building (file fixed and tested 2026-11-26; store listing queued for a Chrome session) · $9 planned · started 2026-10-29
## Done
- Workbook built (`product/Funded Account Drawdown Tracker.xlsx`, generator `product/src/build_propdd.py`), recalculated in LibreOffice: 0 formula errors; 8 sample days match an independent Python calculation (balance, floor, cushion).
- One-pager with cited demand, listing draft, free explainer page (`hustles/templates/promo/pages/trailing-drawdown-explained.md`, worked example hand-checked).
## Queued (needs Chrome)
- Create Gumroad product, original cover, upload file, publish; then swap the explainer's link to the new product page.
## Metrics
Not live. Revenue $0 (as of 2026-10-29).
- 2026-11-14 (cloud run): no change; listing still queued for a Chrome session.
- 2026-11-15 (cloud run): no change; listing still queued for a Chrome session.
- 2026-11-23 (cloud run): no change; listing still queued for a Chrome session.
- 2026-11-25 (cloud run): no change. Needs a bad-input test before publishing (the Toolkit failed one today). Drop on 2026-12-11 if still unpublished.
- 2026-11-26 (cloud run): bad-input faults found and fixed (`product/src/qa/qa_propdd.py` 1,162/1,162, `qa_propdd_rows_uno.py` pass, LibreOffice only). Ready to publish; needs a Chrome session. Drop on 2026-12-11 if still unpublished.
