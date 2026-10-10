# DECISIONS.md — dated log of what changed and why

Newest at the bottom. Changes to risk caps / risk engine / anything touching live orders need Gomes's yes in chat before merge (money rule 9).

## 2026-10-09 — Phase 0 start
- **Fresh start.** Nothing from the earlier Alpaca/Jupyter scaffolding is reused. Repo built from zero.
- **Python 3.12 on Railway, Railpack builder, worker start `python -m engine.worker`.** Chosen for the smallest moving parts; no Dockerfile needed.
- **Dependencies kept to `requests` + `PyYAML`.** Tests use the standard library `unittest` (pytest also runs them). Reason: fewer things to break on deploy; Claude's cloud workspace can't reach PyPI, so tests had to run with no extra installs.
- **Risk engine is deterministic, offline, and the only path to a broker.** Caps: 5% max loss per trade (paper and live), 10% daily loss → no new live entries, 30% drawdown from peak → kill switch (sticky until human reset), no margin, no naked shorts, whole units only, settled cash only, live gate requires live token + live mode. 22 unit tests prove each cap blocks. Paper orders go through the same per-trade cap so paper sizing matches live (rule 7).
- **Second lock in the broker adapter:** `TradierBroker.place()` refuses a live order on the sandbox adapter and vice versa.
- **Live is impossible by construction:** live only if `TRADIER_LIVE_TOKEN` is set AND `LIVE_TRADING_ENABLED=true`. Neither exists now.
- **Shadow fills:** real-time source is Yahoo Finance's public 1-minute chart endpoint (last price, no bid/ask) plus 2 bps slippage, buys up/sells down. Reason: the sandbox is 15-min delayed, the live Tradier token can't be used because it would enable live orders (rule 3), and no free source gives bid/ask. Known gap, logged in STATE.md. Options shadow fills use delayed sandbox bid/ask and are flagged `option_delayed`.
- **Data branch push via GitHub Contents API** with a fine-grained token (`GITHUB_DATA_TOKEN`, Contents read/write on this repo only). Reason: no git binary or SSH key needed on Railway; pushes only to branch `data`, never `main`, so deploys don't loop.
- **Alerts** go to a webhook URL (`ALERT_WEBHOOK_URL`, Discord-style). Silent if unset.
- **Variable names Gomes types into Railway:** `TRADIER_SANDBOX_TOKEN` (now), `ALERT_WEBHOOK_URL` (optional), `GITHUB_DATA_TOKEN` (for snapshots), later `TRADIER_LIVE_TOKEN` + `LIVE_TRADING_ENABLED`.
- **Strategy stages** live in each `config.yaml`; the worker only runs `paper` and `live`. Promotion = editing one line, reviewed via PR.
