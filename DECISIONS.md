# DECISIONS.md — dated log of what changed and why

Newest at the bottom. Changes to risk caps / risk engine / anything touching live orders need Vivek's yes in chat before merge (money rule 9).

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
- **Variable names Vivek types into Railway:** `TRADIER_SANDBOX_TOKEN` (now), `ALERT_WEBHOOK_URL` (optional), `GITHUB_DATA_TOKEN` (for snapshots), later `TRADIER_LIVE_TOKEN` + `LIVE_TRADING_ENABLED`.
- **Strategy stages** live in each `config.yaml`; the worker only runs `paper` and `live`. Promotion = editing one line, reviewed via PR.

## 2026-10-13 — First deploy
- **Railway region moved from Amsterdam (default) to us-east4.** Reason: closer to US markets and Tradier; lower latency for intraday setups.
- **First deploy succeeded.** Logs: 5/5 Tradier sandbox checks passed, branch `data` created, 3 ledger files pushed.
- **Two problems found in the logs, both being fixed before any setup trades paper:**
  1. No Railway volume, so `/ledger` resets on each redeploy. Fix: the worker restores `/ledger` from branch `data` at startup. Chosen over a Railway volume because it costs nothing and GitHub is already the source of truth.
  2. The sandbox account shows $100,000 equity. Sizing off that would break rule 7 (paper sized as if live). Fix: virtual paper equity = chosen paper size + the sandbox's dollar P&L since the baseline. The size itself is Vivek's call.

## 2026-10-13 — Paper size, ledger restore, sticky kill switch (PR, needs Vivek's yes)
- **Paper size: a virtual $1,000 account, whole shares (Vivek's choice).** At $50 the cap is $2.50 a trade and Tradier paper can't do fractional shares, so nothing could trade. Virtual equity = $1,000 + the sandbox's dollar P&L since the baseline. This bends rule 7 on purpose. Every setup also reports "tradeable at $50 live: yes/no" with the reason (`engine/sizing.py`). Results are reported in % and R so they scale.
- **Ledger restore:** the worker pulls `/ledger` from branch `data` at startup, before writing anything.
- **Risk state persists** in `ledger/risk_state.json`: peak equity, start-of-day equity, kill switch, paper baseline. Before this, a restart would have cleared the drawdown peak and the kill switch.
- **Kill switch reset** happens only when Vivek sets `KILL_SWITCH_RESET` to *today's* New York date and the bot restarts. A stale value is ignored.
- **Off-hours heartbeat push** every 60 minutes, so the city can show the bot is alive overnight.
- Known edge case: if Tradier resets the sandbox account, the virtual equity jumps. To fix it, change PAPER_EQUITY (that re-baselines) or delete `risk_state.json` from branch `data`.

## 2026-10-13 — LIVE_EQUITY raised to $1,000
- Vivek clarified: the $50 cap (money rule 1) is his own money going in, not the account size when he actually flips to live. He expects hustle/trading profit to have grown it to roughly $1,000 by then.
- `LIVE_EQUITY` default changed 50 -> 1000. "Tradeable at live size" flags (`engine/sizing.py`) now report against $1,000. Easy to raise again if the estimate changes before go-live. Money rule 1's $50 cap is unchanged.

## 2026-10-13 — Compound City (Phase 0 step 5)
- **The city is a hand-built artifact** (`city/compound-city.html`), not the Dashboard type. Reason: the brief calls for a game-style pixel town with characters, movement, and day and night, which the Dashboard type doesn't do. The Ledger view inside it covers the charts and tables.
- **State lives in the artifact's database**, not in the page. Residents write with ArtifactData; Vivek answers City Hall on the page. Access rule: anyone who can open the page reads; only owner/editors write.
- **Seeded honestly:** bot/Depot, Treasury, Watchtower, City Hall tasks and the decision timeline are real. Residents' activity, setup metrics, hustle stalls, the trade log and the newsstand note are SAMPLE, with dashed gold outlines, until real runs replace them.
- **Day and night follow market hours (PT):** pre-market dawn, market-open day, after-hours dusk, night. Lights dim if the heartbeat is older than 25 min in market hours or 150 min otherwise.
- **Railway watch patterns** limit redeploys to bot code (`engine/`, `strategies/`, `scripts/`, requirements, railway.toml, .python-version). City or docs commits no longer restart the bot.
- **Railway source reconnected** as `vivekgomathinayagam-ux/Trading-lab` on branch `main`. The earlier lowercase name with no branch set never auto-deployed after the first build.

## 2026-10-13 — Owner, capital, paper autonomy, first real hustles (from Vivek)
- **Owner is Vivek Gomathinayagam.** The project runs on Gomes's Claude account, but every file, credit and write-up names Vivek (resume use). "Gomes" was replaced by "Vivek" across the repo.
- **Money rule 1, as Vivek updated it:** $1,000 of Vivek's money for live trading only; $50 for operations (Claude Pro). Railway is paid by his existing subscription. Hustle income goes to the live account before go-live, and he wants to start with more than $1,000. Never ask for more deposits. All other money rules are unchanged. The project-instructions text should read: "1. My money in this project: $1,000 for live trading only and $50 for operating costs (Claude plan). Railway is already paid. Never ask me to deposit more. Hustle income goes to the live account."
- **Paper trading needs no confirmations.** The bot trades paper on its own, and every order and fill is logged and shown in the Ledger. Rule 9 (Vivek's yes before merging changes to risk caps, the risk engine or live-order code) still applies.
- **The sample hustles were placeholders, so they couldn't be approved.** They've been replaced with 4 real one-pagers and an income-routing question, all answerable at City Hall.

## 2026-10-21 — Pine approved; Claude Pro covered by Vivek
- **Pine Script commissions approved** (in chat). Vivek wants Claude to run the Fiverr store end to end because he's too busy to message clients.
- **Fiverr's rules shape how:** its Integrity and Authenticity standards forbid having "someone else represent you in your Gig... without clearly stating who they are", bots or automated processes for mass messages, and access "through unauthorized methods". So, if Claude runs the store: the gig says plainly that an AI assistant handles messages and code, it only answers inbound buyers (no outreach), at human pace, through Vivek's own logged-in browser. The risk of an account restriction still sits on Vivek's name.
- **Claude Pro:** Vivek pays it himself for now (he'll say if that changes). The income-routing question is answered "no": all hustle income goes to the live fund.

## 2026-10-24 — Crypto Pier: BTC/ETH research lab (from Vivek: majors, not meme coins)
- **Scope:** BTC and ETH, spot, long only. No leverage, perpetuals, futures or shorting (money rule 4). Meme coins dropped: on-chain studies flag most new Solana tokens as rug pulls, and new-launch scalping is a speed race a polling bot loses. Day trade, swing, or both, whichever the evidence supports.
- **Where tests run: GitHub Actions** (`.github/workflows/crypto-lab.yml`). Weekly (Saturdays 09:17 UTC), on any change under `lab/`, and on demand. It uses the built-in repo token, no secrets, and saves results to branch `data` under `backtests/crypto/`. Reason: Claude's workspace can't reach market data, and keeping research off the Railway bot means a lab bug can't stop trading.
- **Data:** Coinbase Exchange public candles (1h and 1d), from 2017-01-01. Lab code in `lab/crypto/` (pandas + numpy, separate from the bot's two dependencies). 18 unit tests cover next-bar fills, fees on both sides, stop fills including gaps, 5%-risk sizing, and look-ahead (changing future bars must not change past signals).
- **Costs:** headline uses Robinhood's API taker rate, up to 0.95% per side at the entry tier, plus 0.05% slippage. Also reported: 0.40% (an assumed cheaper venue) and slippage-only.
- **Sizing:** 5% max loss per trade (the rule's ceiling) and 2%. At 5%, normal losing streaks alone break the 20% drawdown gate, so 2% is the realistic size for these rules.
- **Results (7 families × 2 coins, 22 variants each):** nothing passed. Day-trading rules lose 85–90% a year after fees and had no edge before fees; 4h EMA and RSI(2) also fail. Only daily trend following survives fees (BTC breakout 2% risk: +17.1%/yr, −21.7% max drawdown, Sharpe 0.99 vs buy-and-hold 1.0), and its gains come from 3 big trades. Retired: 4h EMA, both day-trade rules, RSI(2). Kept in backtest for refinement: 100-day trend and 20/10 breakout on BTC and ETH. Full report: `data:backtests/crypto/latest/REPORT.md`; spec: `strategies/crypto_pier/spec.md`.
- **Design lesson for the bot:** the ETH breakout's −96% drawdown came from a stale fixed stop hit by Coinbase's 21 June 2017 flash crash (ETH near $0.10 for a moment). Before any crypto rule goes to paper: trailing or close-based exits, no deep resting stop orders on a single venue. The lab now flags such bars and reports each rule's worst day.
- **City:** the park becomes the **Crypto Pier** (8 desks, a 24/7 sign). Pier setups are `agents/<id>` with `kind: setup` and `venue: pier`.
- **Autonomous research:** a weekly scheduled task (Pier & Floor Researcher) reads the newest results, runs the next experiment from the research queue on a `lab/` branch, merges lab-only changes after tests pass, updates the city, and messages Vivek only at checkpoints (a rule passes the screen, something breaks, or a decision is his). It never touches the risk engine, live-order code or secrets.
- **Flag for Vivek:** the GitHub repo is public. Recommendation: make it private (GitHub → repo Settings → General → Change visibility). Actions still works (2,000 free minutes a month on private repos; a run takes about 6). The sandbox account number has been removed from STATE.md, but it remains in git history.

## 2026-10-25 — Crypto ETF/options pattern test (Vivek asked: can crypto ETFs + options print short-term cashflow?)
- **Request:** Vivek asked whether a repeatable short-term pattern on BTC/ETH could be traded via crypto ETFs (IBIT, FBTC, BITO, etc.) using long calls/puts for defined-risk cashflow, using "decades" of backtest history.
- **Reality check:** there's no decades-long history for this instrument. Usable BTC/ETH data runs ~2017-2026 (what the lab already has). The ETFs are new (BITO Oct 2021, spot ETFs Jan 2024) and their listed options have even less history, so a direct ETF-options backtest isn't possible. Approach taken instead: test short-horizon directional patterns on real BTC/ETH spot (what an options trade would be trying to capture), since these ETFs track spot closely.
- **3 new patterns, pre-registered, 16 variants total:** drop-bounce (mean reversion after a ≥10% 1-day drop), momentum-burst (continuation after a ≥15% 3-day move), squeeze-breakout (breakout from a volatility contraction). Each holds 3-15 days — short enough to map to a short-dated option.
- **Result: all three fail the screen on BTC and ETH after Robinhood-level costs.** Drop-bounce and squeeze-breakout lose money after costs. Momentum-burst is the only one with positive expectancy (profit factor 1.5-3.2 depending on cost/sizing slice) but its Sharpe (0.3-0.5) stays below just holding the coin, and it still fails drawdown/out-of-sample checks. None of the three are evidence an options trade would work — real options add theta and IV cost on top of a spot edge that doesn't clear the bar by itself. Full report: `data:backtests/crypto/latest/REPORT.md`; detail in `strategies/crypto_pier/spec.md`.
- **Research queue updated:** if momentum-burst is refined further and clears the screen on spot, the next step before paper is pricing it as an actual options trade (strike/expiry, theta cost over the hold, real bid/ask) — a spot pass alone wouldn't be enough.
