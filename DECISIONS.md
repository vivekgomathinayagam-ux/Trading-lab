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

## 2026-10-25 — Day-trade desks: ORB + EMA + volume spike on SPY/QQQ and their 3x ETFs (from Vivek)
- **Vivek's rules:** keep paper trading ORB and EMA; focus on TQQQ and the other leveraged and inverse ETFs for SPY and QQQ; on every day-trade setup, use 1-minute volume to spot big moves; target +5% a trade and let it compound; backtest now, and paper trade regardless of the result, never stopping the experiment. Crypto excluded.
- **Pre-registered** in `strategies/daytrade/spec.md` before any data was pulled. Symbols: SPY, QQQ, TQQQ, UPRO, SQQQ, SPXU. Long only (inverse ETFs cover bearish days). Stop -2.5% (half the 5% target). One entry per desk per day (cash-account settlement). Flat by 15:55 ET. Volume spike = 3x the median of the prior 20 one-minute bars AND 1.5x the same minute's 5-session average. Paper desks: ORB + volume, EMA 9/21 + volume, Volume spike. Backtest-only comparisons: ORB plain, EMA plain, Volume spike 2x.
- **One code path:** `strategies/daytrade/core.py` (pure Python) is used by both the lab (`lab/floor/`) and the bot (`engine/daytrade_runner.py`), so paper trades exactly what was backtested. 18 new tests. A null test on 8 random-walk datasets showed about zero or slightly negative expectancy after costs for every rule, so the engine isn't leaking future data.
- **Backtests on GitHub Actions** (`floor-lab.yml`): after every weekday close, on lab changes, and on demand. Yahoo keeps only ~30 days of 1-minute bars, so the workflow archives them on branch `data` (`backtests/data/etf1m/`) and the history grows every day. Also runs a 5-minute check over 60 days, and measures since 2010 how often each ETF traded +5% above its open in one day.
- **Paper:** each desk is a virtual $1,000 book that compounds on its own. Results are judged on shadow fills at the live Yahoo price plus slippage; the Tradier sandbox gets matching paper orders for plumbing. Every entry passes the risk engine. The runner only builds paper orders, and the bot never builds a live adapter, so no live-order code or risk caps changed (rule 9 not triggered).
- **Why nothing traded Oct 13-25:** the bot ran the whole time (paper baseline locked at the Oct 14 open), but no setup was set to paper, and no scheduled task existed to start one. Phase 0 paused at step 5 for Vivek's go-ahead, and that pause wasn't made visible. Fixed: the desks run on paper from Oct 26, and a daily close task tracks them.
- **First backtest (1-min, Oct 1-23 2026, 17 sessions, $1,000 per desk, run 40270243831):** no edge yet, and the sample is tiny. ORB + volume 12 trades, −2.65%, PF 0.55. EMA 9/21 + volume 11 trades, −2.51%, PF 0.33. Volume spike 17 trades, +1.13%, PF 1.2. The +5% target was hit 0 times on the paper desks; most trades closed at 15:55. Triple slippage turns all three negative. The 5-min check over 37 sessions (Sep 2-Oct 23) is negative for all three paper desks. Since 2010, +5% above the open in one day happened on 0.17% of SPY days, 0.19% of QQQ days, and 3-10% of 3x-ETF days, while −2.5% happened on 19-31% of 3x-ETF days. So a +5%/−2.5% day trade on these ETFs mostly ends at the close or the stop; the target is rare. Paper runs anyway, as Vivek asked; rules are not tuned on this window.
- **Daily tracking:** scheduled task "Accountant (daily close)", weekdays 2:40 PM PT, automatic approval. It computes paper stats per desk vs SPY, updates the city and STATE.md, proposes a retirement at City Hall when a desk's rolling 30-trade expectancy turns negative, and messages Vivek only at checkpoints (first paper trade, a +5% hit, a desk down 10%, a bot problem, Friday scorecard).
- **Bot redeployed** (commit 048b586, deploy 5eab4bc6): logs show 5/5 checks, ledger restored, three desks on paper, warm-up on all six ETFs through Oct 23 15:59 ET.

## 2026-10-26 — Paper day 1 (Accountant daily close)
- First paper trades ever: all three desks traded once, all closed at the end of the day (no stop, no +5% target). ORB + volume SPY +$0.52 (+0.05%), Volume spike SPY −$1.85 (−0.19%), EMA 9/21 + volume SQQQ −$4.09 (−0.41%). SPY buy-and-hold +0.37%. Sample: 3 trades, so this says nothing yet about edge.
- Gap found (not a bug in the rules, a timing difference): paper end-of-day exits filled at 15:56:43 ET, about 1.7 min after the spec's 15:55, because the runner acts on the completed 15:55 bar. Logged under Known gaps; any change touches engine/ and needs Vivek's yes.
- City: desks now show PAPER metrics in `metrics`; the backtest numbers moved to `backtest_metrics`.

## 2026-10-26 — GEX setup unblocked (Vivek asked why it's still "idea")
- **Why it was stuck:** the old blocker note (FlashAlpha free tier blocks SPY/QQQ/SPX; no historical options data) was correct when written but is now stale.
- **Unblocked:** Vivek's connected Skylit gives both missing pieces — `heat_historical_heatmap` (real per-strike dealer gamma/vanna, 365 days back) and `option_chain`/`contract_history` (real historical options pricing to simulate spread fills). Cost is trivial against the account's ~$105 balance.
- **Still blocking an actual build:** Vivek's four filters (0DTE GEX share, IV ratio, pin score, net GEX regime) are his own design and were never written down in this repo, only named. Asked him for the exact definitions rather than guessing — a wrong guess would quietly test something other than his strategy. Logged candidate interpretations in `strategies/gex_spreads/spec.md` for him to correct or confirm.
- **Also flagged:** options-leg shadow fills still price off the delayed Tradier sandbox quote, not real-time — fine while nothing options-based is on paper, but must be fixed (or covered by Skylit's option_chain for a real-time-enough read) before GEX spreads go to paper, or paper results would be wrong.

## 2026-10-26 — GEX filters: proposed spec for Vivek's review (no build yet)
- **Vivek's instruction:** use best-guess definitions for his five filters (0DTE GEX, GEX Share, IV Ratio, Pin Score, Net GEX Regime), label every unverified formula and threshold as an assumption, check existing code, docs and Skylit first, keep raw metrics separate from signals, make thresholds configurable, propose a backtest plan, and **not** implement, deploy or trade until he reviews.
- **What was checked:** repo, notes and the FlowbyBobby rulebook define none of the five formulas. ~22 Skylit credits (≈$0.02) of live probes verified the real fields: per-strike gamma (live + 365 days back), a live-only per-expiration matrix, a live-only net/flip summary, Tempest SVX with ~2 years of daily history, end-of-day-only historical option chains (no bid/ask), and intraday contract bars only 30 days back.
- **Findings that change the plan:** (1) GEX history is 365 days, short of the 2-year gate, so results will be preliminary. (2) Old 0DTE spreads can't be priced from real quotes, so Stage B uses modeled prices with 1×/2×/3× costs plus a daily real-price archive. (3) Our flip calc (758) didn't match Skylit's summary (766.04) on the same snapshot, so it must be validated against Skylit's before use. (4) Skylit `value` units are undocumented and look normalized per symbol; thresholds are ratios, signs or percentiles only. (5) SPX verticals fail the 5% cap at $1,000; the live-tradeable version is SPY $1-wide with ≤$0.50 risk.
- **Done:** `strategies/gex_spreads/spec.md` (proposal, every item tagged VERIFIED / ASSUMPTION / VERIFY WITH SKYLIT, 8 open questions) and `config.yaml` (all thresholds as params; `stage: idea`, so the bot never loads it).
- **Next, only after Vivek answers:** Stage A (do the filters predict the underlying's range, pin and trend? ~$5 of Skylit credits, no option prices), with a pre-registered kill criterion before any options work.

## 2026-10-26 — Paper data audit (Vivek: does the Tradier 15-min delay taint paper results?)
- **Finding:** no. The day-trade desks take signals from Yahoo 1-min bars and price fills at Yahoo's live last trade + slippage. Tradier sandbox only gets mirror orders, which aren't used for results. Yahoo prices on Oct 26 matched Skylit's 1-second spot within $0.03 at each SPY fill.
- **Real gaps found:** quote timestamps not recorded; stop/target exits would fill at the live price, not the rule level; EOD exit timing differs from the backtest; Yahoo is unofficial (no bid/ask, robots-disallowed, no SLA).
- **Proposed (not done, waiting for Vivek's yes):** log quote provenance + age; a Skylit cross-check at each fill (~6 credits/day); exit at rule levels like the backtest; EOD at the 15:55 open; Skylit fallback for marks only. No production endpoint, no live token.
- **Results so far (1 day, 3 trades):** retained, labeled "Yahoo real-time + assumed slippage, quote time not recorded". Full report: `docs/audits/2026-10-26-paper-data-audit.md`.

## 2026-10-26 — Hustle department runs on its own (from Vivek)
- **Vivek's rule:** Claude runs the whole hustle department with no approvals and no setup questions. Anything that needs Vivek by hand gets dropped. Keep trying ideas until one works, then scale it and keep going. The only thing Claude may ask for is starting funds for a hustle Claude can run alone that is close to certain to work, and Vivek wants that to be extremely rare.
- **Two limits Claude can't remove, written into `hustles/OPERATING.md`:**
  - **Payout setup:** no store pays out until the account owner verifies his own identity, tax form and bank. Claude asks for this once, as one bundled City Hall item, only when a product is ready to sell.
  - **No passwords in chat** (money rule 3). Signed-in sites run through Vivek's Chrome in interactive sessions only.
- **Money rules unchanged:** Claude never moves or spends money (start cost $0), and Vivek moves income to the live fund. The honesty rules also stay: no fake reviews, no spam, no impersonation, no signal products, and each platform's terms are followed.
- **Dropped:**
  - **Pine commissions on Fiverr:** custom orders need live client chats, and Fiverr requires the owner to represent his own gig.
  - **Discord bot clients:** need clients, server permissions and deadlines.
  - **LinkedIn build log:** LinkedIn's terms ban automated posting.
- **Started:** Trader Toolkit, ready-made digital products (trade journal and options risk spreadsheets, ready-made Pine indicators). They sell without customer contact.
- **Records:** hustle money goes in `hustles/LEDGER.csv` on main, not the data branch. The bot's snapshot pushes rewrite `data:ledger/`, so hustle rows there could be overwritten.
- **Schedule:** "Hustle Department" runs Tue and Fri at 8:43 AM PT with automatic approval. It replaces the planned Wednesday Hustle Scout.

## 2026-10-26 — Claude assigns each scheduled task its model (from Vivek)
- **Vivek's rule:** Claude picks the right model for each task, now and for future tasks, instead of using the top model for everything.
- **Applied:** Researcher stays on Opus 5.5 (backtest rigor). The Accountant moves to Sonnet 5.5 (routine). The Hustle Department moves to Sonnet 5.5 and now runs daily at 8:43 AM PT while products are being built, then switches itself to Tue and Fri once everything is live. That gives about 3x more hustle work for roughly the same usage, since Sonnet costs less per run.
- **Policy and table:** see STATE.md, "Models for scheduled tasks".

## 2026-10-26 — Approved paper-data fixes built (Vivek's decisions)
- **Built and deployed (d8f0b896):**
  - Fix 1: quote time, quote age (flag > 90 s) and signal-bar time on every entry and exit.
  - Fix 2: Skylit cross-check of all six ETFs at each fill (flag > 0.05%; one 1-credit call per step with fills).
  - Fix 4: every exit records the backtest rule price next to the paper price, including the 15:55 open vs the ~15:56:43 live price. Record only.
  - Fix 5: if Yahoo fails, open positions are valued with Skylit and all new entries pause until Yahoo is back.
  - Fix 6: Tradier mirroring unchanged, sandbox token only.
  - All of it goes to a new file, `ledger/daytrade_fills.csv`.
- **Unchanged:** signals, sizing, fill prices in normal operation (a test proves identical trades with and without the checks), the risk engine, live-order code.
- **Fix 3 not built:** Vivek rejected exact-price stop/target fills. A realistic model (stop-market with extra slippage; limit target fills only if price trades through) is proposed in `docs/proposals/2026-10-26-fix3-stop-target-model.md` for his review.
- **Results:** Oct 26 trades kept, labeled `preliminary`. A fresh evaluation (`eval-1`, desks reset to $1,000) starts after one live session verifies the new logging and the Skylit check (needs `SKYLIT_API_KEY`).
## 2026-10-26 — Research desk charter: the Researcher becomes the quant desk (from Vivek)
- **Vivek's rule:** backtest only when a strategy is first adopted; after that it lives in paper trading, every day. Test the five identified setups for a month on paper, alone and in combination. The Researcher studies the paper P&L and all data, finds the best setup combinations, and adds new indicators or setups if they help. It acts as a top-level quant analyst and trader whose whole job is to find and capture edge.
- **The five setups** (Vivek didn't list them; Claude's reading): ORB + volume, EMA 9/21 + volume, Volume spike, CVD turn, GEX-filtered verticals. SPY buy-and-hold stays the control.
- **Charter and queue:** `research/CHARTER.md`, `research/QUEUE.md`, `research/VARIANTS.md`, `research/combos.md`.
- **Rules that keep the month honest:** desk rules are frozen (a change is a new desk key); no retirement for performance inside Month-1 (Oct 26 to Nov 25); combos and new ideas are pre-registered and judged on forward days only; every variant is counted; verdicts come with bootstrap confidence intervals. One entry per desk per day caps a desk at about 23 trades in the month, so most verdicts will be "inconclusive, keep running".
- **Backtest vs paper:** floor-lab's daily Actions run stays as the 1-minute data archiver (Yahoo keeps only about 30 days) and as the parity replay of each paper day. The Oct 1-23 numbers are the frozen reference.
- **Permissions:** the Researcher may add new day-trade rules to `strategies/daytrade/core.py` (new classes only), create new setup folders, and put new setups in paper and deploy them outside market hours. It may not touch the risk engine, broker adapters, order code, risk caps, any `live` stage, secrets or Railway variables, or the existing desks' rules. Other `engine/` changes go to Vivek as an unmerged pull request plus one non-blocking City Hall item. Rule 9 is untouched.
- **GEX:** the 8 open questions stay open but no longer block. The Researcher proceeds on the spec's labeled assumptions and reports results as "Claude's definitions". Skylit credits (about $105 balance, included in the plan): at most 8,000 a week, balance kept above 20,000.
- **Schedule and model:** new task "Researcher (quant desk)" on Opus 5.5, Wednesdays (build) and Saturdays (review) at 3:34 PM PT, after the close and the Accountant. It replaces the Saturday 6:34 AM task, which had no Skylit access. The old task still shows as enabled: both attempts to delete or disable it were blocked by the auto-mode classifier, so Vivek needs to do it or confirm in chat.

## 2026-10-26 — Skylit key live in the bot (Vivek)
- Vivek created a separate read-only key for the bot and added it as `SKYLIT_API_KEY` in Railway (separate from the key used by the Claude connector, so each can be rotated alone). First attempt was saved under the wrong name (`skylit_api_token`) and was still unapplied; he fixed the name and deployed. Deploy 4202b52a (main at 30e2db8, docs only): logs show 5/5 Tradier checks, ledger restored (7 files), `CHECK skylit spot: ok, 6/6 symbols`, desks warmed up through Oct 26 15:59 ET. The Skylit price cross-check and the Yahoo-down fallback are on from the Oct 27 open.

## 2026-10-26 — Skylit becomes the Researcher's own edge project (from Vivek)
- **Vivek:** he provides resources, not finished strategies. The Researcher must use Skylit to develop setups itself, through its own research and paper trading, and keep improving them.
- **What changed:**
  - The GEX spec's 8 questions for Vivek are closed. The Researcher defines every metric itself.
  - New charter section on Skylit: all of Heatseeker, Flowseeker and Tempest are in scope. Research path: measure what predicts, pre-register, back-test once, paper, then improve through new versions.
  - Credit discipline: cache raw pulls on the data branch, use batch tools, sample at fixed times. Budget: research 20,000 credits a week, bot up to 500 credits a day, balance above 20,000.
- **New permission:** the Researcher may add read-only Skylit data plumbing in `engine/` (for example `engine/skylit_feed.py`, plus additive changes in the day-trade runner and market data) so its Skylit desks can paper trade. Tests must show existing desks trade identically. Orders, fills, the risk engine, brokers, caps and live stay off-limits, so money rule 9 is not triggered. An options order path is still order code and goes to Vivek as a PR.
- The Researcher's scheduled prompt was updated to match.

## 2026-10-27 — Trader Toolkit v1 built; moved to ready (Hustle Department)
- Built and tested two products: Options Day Trader Journal.xlsx and Options Risk and Position Size Calculator.xlsx (LibreOffice recalculation, 0 errors, outputs hand-checked). Listing, FAQ and AI disclosure written for Gumroad at $12.
- Pine indicator pack dropped from v1: a script can't be compile-tested here and an untested script should not be sold. Draft kept unlisted.
- Stage: ready. Posted the single bundled City Hall item `t-store-setup` (Gumroad account, identity, tax form, payout). Nothing else needs Vivek.
- Schedule unchanged (daily): second experiment to be researched next run.

## 2026-10-27 — Trader Toolkit published; standing orders from Vivek
- Published on Gumroad at $12 (https://vivekgo8.gumroad.com/l/aobhdm) from Vivek's signed-in Chrome. Cover and thumbnail are original art with no results claims (Vivek: attention-grabbing, not tied to results; I kept it honest). Summary line and 8 tags added; the product is set for Gumroad search/Discover.
- Standing orders (OPERATING.md): decide small issues without asking; contact Vivek only after a sale; promote by every honest channel. Fixed lines unchanged: no fake reviews/accounts/sales, no spam, no profit claims, platform rules respected, I never move or spend money, I never create accounts or enter passwords.
- Sale alerts: Gumroad emails Vivek on each sale. Scheduled runs are cloud-only and cannot open his Chrome, so the department will also check for sales in interactive sessions and from the Gumroad email/notification path when available.
- Promotion plan: hustles/templates/promo/PLAN.md.

## 2026-10-28 — Hustle Department run: promotion and Plan Pack
- Measure: no reachable sales data from a cloud run (Gumroad page fetch needs approval nobody can give unattended). No ledger row; nothing estimated.
- Promote: published free search-friendly pages in the repo (`hustles/templates/promo/pages/`): position-size cheat sheet and calculator, both linking to the product, no results claims. GitHub Pages cannot be enabled from here, so the HTML page is queued for an interactive session.
- Build: Plan Pack workbook (pre-trade checklist with GO/WAIT, daily plan, weekly review) tested in LibreOffice. Decision: add it to the existing Toolkit at the same $12 price as one change; a cheaper standalone and a free funnel product are later tests. Only one active experiment, so no new hustle was started; research showed Gumroad trading-plan templates are crowded, so a separate product is not justified yet.
- Community drafts queued (Chrome only, each community's rules first).
- Cadence unchanged: daily while promotion/building work remains.

## 2026-10-28 — Researcher build run (Wednesday)
- **Tools built:** `lab/floor/paper_report.py` (per-desk stats, bootstrap CIs, breakdowns, MAE/MFE, correlations) and `lab/floor/replay.py` (parity replay), both unit-tested.
- **Parity Oct 26-27:** 4 of 5 trades match. The miss (ema_vol Oct 26: lab SPXU 12:40, bot SQQQ 12:50) comes from Yahoo dropping SPXU minutes 12:32 and 12:34 in the archive, which merged two 5-minute buckets. UPRO and SPXU miss 1-6% of minutes every day. Not a lab/bot code difference; a fragility in the frozen rule.
- **New paper desks from Oct 29 (pre-registered and committed before any test, commit 5487e5a):**
  - `ema_vol_v2`: ema_vol with clock-based buckets (bug fix as a new key; `ema_vol` unchanged and still running).
  - `cvd_spy` and `cvd_tqqq`: Vivek's CVD turn. Delta approximated by close location on 1-minute bars; 3-minute clock candles; buy turn from the 5-candle CVD low (skipped on a candle >3x the session's median range), exit on the sell turn or the shared stop/target/15:55.
- **One backtest (Oct 1-27, 19 sessions):** cvd_spy 19 trades, −0.006%/trade [−0.07, +0.06]. cvd_tqqq 19 trades, +0.47%/trade [+0.19, +0.78], PF 10.4; survives 2x (+0.37%) and 3x (+0.28%) costs; random same-length entries in the same window made +0.11%. An independent pandas re-implementation matched all 38 trades exactly, so it is not a code bug. But it is the best of 6 symbols tried (QQQ +0.07, UPRO 0.00, SQQQ −0.27, SPXU −0.08), from one month in which Nasdaq mornings drifted up. Verdict: interesting, not trusted; only forward paper counts.
- **Engine:** no engine/ file changed. Two hooks added in `strategies/daytrade/core.py` (`Rule.observe`, `Rule.reset`; base versions do nothing) so a rule can exit on its own signal. Proof the original desks are untouched: identical trades to the frozen floor-lab run (100 of 100) with and without the new desks, plus unit tests in lab and through the bot runner.
- **Skylit pilot 1 (pre-registered in `research/skylit/STUDY.md`):** 62 sessions of 10:00 ET boards for SPY/QQQ. The close moved toward the king strike 46% of days [37, 55]; net-gamma sign made no difference to the rest-of-day move; positive kings did not pin harder. Nothing to trade. Credits used this run: 341 (balance 104,217). Raw pulls cached on branch `data` under `research/skylit/raw/` (commit a92f498); a spot check of one board re-pulled from Skylit matched the subagent transcription exactly, and the daily closes match Yahoo within 0.04%.
- Desks in paper: 6 of 8.
