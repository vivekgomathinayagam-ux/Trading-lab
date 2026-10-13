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

## 2026-10-13 — First deploy
- **Railway region moved from Amsterdam (default) to us-east4.** Reason: closer to US markets and Tradier; lower latency for intraday setups.
- **First deploy succeeded.** Logs: 5/5 Tradier sandbox checks passed, branch `data` created, 3 ledger files pushed.
- **Two problems found in the logs, both being fixed before any setup trades paper:**
  1. No Railway volume, so `/ledger` resets on each redeploy. Fix: the worker restores `/ledger` from branch `data` at startup. Chosen over a Railway volume because it costs nothing and GitHub is already the source of truth.
  2. The sandbox account shows $100,000 equity. Sizing off that would break rule 7 (paper sized as if live). Fix: virtual paper equity = chosen paper size + the sandbox's dollar P&L since the baseline. The size itself is Gomes's call.

## 2026-10-13 — Paper size, ledger restore, sticky kill switch (PR, needs Gomes's yes)
- **Paper size: a virtual $1,000 account, whole shares (Gomes's choice).** At $50 the cap is $2.50 a trade and Tradier paper can't do fractional shares, so nothing could trade. Virtual equity = $1,000 + the sandbox's dollar P&L since the baseline. This bends rule 7 on purpose. Every setup also reports "tradeable at $50 live: yes/no" with the reason (`engine/sizing.py`). Results are reported in % and R so they scale.
- **Ledger restore:** the worker pulls `/ledger` from branch `data` at startup, before writing anything.
- **Risk state persists** in `ledger/risk_state.json`: peak equity, start-of-day equity, kill switch, paper baseline. Before this, a restart would have cleared the drawdown peak and the kill switch.
- **Kill switch reset** happens only when Gomes sets `KILL_SWITCH_RESET` to *today's* New York date and the bot restarts. A stale value is ignored.
- **Off-hours heartbeat push** every 60 minutes, so the city can show the bot is alive overnight.
- Known edge case: if Tradier resets the sandbox account, the virtual equity jumps. To fix it, change PAPER_EQUITY (that re-baselines) or delete `risk_state.json` from branch `data`.

## 2026-10-13 — LIVE_EQUITY raised to $1,000
- Gomes clarified: the $50 cap (money rule 1) is his own money going in, not the account size when he actually flips to live. He expects hustle/trading profit to have grown it to roughly $1,000 by then.
- `LIVE_EQUITY` default changed 50 -> 1000. "Tradeable at live size" flags (`engine/sizing.py`) now report against $1,000. Easy to raise again if the estimate changes before go-live. Money rule 1's $50 cap is unchanged.

## 2026-10-13 — Compound City (Phase 0 step 5)
- **The city is a hand-built artifact** (`city/compound-city.html`), not the Dashboard type. Reason: the brief calls for a game-style pixel town with characters, movement, and day and night, which the Dashboard type doesn't do. The Ledger view inside it covers the charts and tables.
- **State lives in the artifact's database**, not in the page. Residents write with ArtifactData; Gomes answers City Hall on the page. Access rule: anyone who can open the page reads; only owner/editors write.
- **Seeded honestly:** bot/Depot, Treasury, Watchtower, City Hall tasks and the decision timeline are real. Residents' activity, setup metrics, hustle stalls, the trade log and the newsstand note are SAMPLE, with dashed gold outlines, until real runs replace them.
- **Day and night follow market hours (PT):** pre-market dawn, market-open day, after-hours dusk, night. Lights dim if the heartbeat is older than 25 min in market hours or 150 min otherwise.
- **Railway watch patterns** limit redeploys to bot code (`engine/`, `strategies/`, `scripts/`, requirements, railway.toml, .python-version). City or docs commits no longer restart the bot.
- **Railway source reconnected** as `vivekgomathinayagam-ux/Trading-lab` on branch `main`. The earlier lowercase name with no branch set never auto-deployed after the first build.
