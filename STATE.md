# STATE.md — Compound City

_Read this first. Updated by every session and scheduled task. Times are America/Los_Angeles._

**As of:** 2026-10-26 17:50 PT (price provenance deployed)
**Previously:** 2026-10-26 14:50 PT (daily close, paper day 1: first 3 paper trades, all closed at the end of day; no +5% hits; bot healthy, kill switch off)

## Phase
Phase 0 — building from zero. See the Phase 0 checklist below.

## What runs where
| Thing | Where | Status |
|---|---|---|
| Bot (worker) | Railway, project `compound-city` (6e2d45ea), service `bot` (94c0bd23), env `production`, region us-east4 | **running**; deploys from `main` |
| Code | GitHub `vivekgomathinayagam-ux/Trading-lab`, branch `main` | pushed |
| Ledger snapshots | branch `data`, folder `ledger/` | first push 2026-10-13 21:10 UTC |
| Crypto Pier lab | GitHub Actions `crypto-lab` (weekly Sat 09:17 UTC + on `lab/` changes); results on branch `data`, `backtests/crypto/latest/` | first run 2026-10-24: nothing passed |
| City (visual) | Artifact **Compound City**: https://claude.ai/artifact/TfjmHPyajJQfFdXrWDrPZm (source `city/compound-city.html`) | live, partly SAMPLE |
| Desk | folder "Compound City" on Vivek's Mac (iCloud) | connected, empty |

## Mode
**paper** (Tradier sandbox). Live impossible: no live token in Railway.

## Treasury (capital rules set by Vivek, 2026-10-13)
- **Live trading fund:** $1,000 of Vivek's money, for live trading only. Not deposited yet. Hustle income is added here before go-live; Vivek wants to start live with more than $1,000.
- **Operations fund:** $50 for running costs (Claude Pro $20/month). Runway: 2.5 months. Not deposited yet.
- **Railway:** paid by Vivek's existing subscription, outside both funds.
- Never ask Vivek to add money beyond these. Hustle income: $0. Trading P&L: $0.
- Oct 21: Vivek pays Claude Pro himself for now (he'll say if that changes), so all hustle income goes straight to the live fund. The $50 operations fund is untouched.
- **Paper trading is fully autonomous:** no trade confirmations, ever. Every paper order and fill is logged in `ledger/trades.csv` and shown in the city's Ledger view.

## Setups (the tournament)
### Day-trade desks (spec `strategies/daytrade/spec.md`; SPY, QQQ, TQQQ, UPRO, SQQQ, SPXU; +5% target, -2.5% stop, 1-min volume spike)
| Desk | Stage | Backtest 1-min Oct 1-23 (17 sessions, $1,000) | Paper so far (**PRELIMINARY**: before price provenance; kept, not judged) | Notes |
|---|---|---|---|---|
| ORB + volume | **paper from 2026-10-26** | 12 trades, −2.65%, PF 0.55, +5% hits 0 | 1 trade, +0.05%, vs SPY −0.32 pts (as of Oct 26 close) | 09:30-09:45 range breakout on a volume-spike bar |
| EMA 9/21 + volume | **paper from 2026-10-26** | 11 trades, −2.51%, PF 0.33, +5% hits 0 | 1 trade, −0.41%, vs SPY −0.78 pts (as of Oct 26 close) | 5-min EMA cross with a 1-min volume spike in that bucket |
| Volume spike | **paper from 2026-10-26** | 17 trades, +1.13%, PF 1.2, +5% hits 0 | 1 trade, −0.19%, vs SPY −0.56 pts (as of Oct 26 close) | spike bar closes up, above VWAP and the prior 15-bar high |
| ORB plain / EMA plain / Volume spike 2x | backtest only | +0.37% / +0.46% / +0.28% | — | comparisons |
| SPY buy-and-hold | benchmark | −0.58% same window | +0.37% (762.35 → 765.19, as of Oct 26 close) | control |
**Evaluation status (Vivek, 2026-10-26):** Oct 26 trades are labeled `preliminary` (Yahoo real-time + assumed slippage, no quote time recorded). A fresh evaluation starts once the new logging is verified in a live session: every fill in `ledger/daytrade_fills.csv` has quote time, age, bar time, and a Skylit cross-check within 0.05% (needs `SKYLIT_API_KEY`). Then: set `evaluation:` in `strategies/daytrade/config.yaml` to `eval-1`, archive the preliminary ledger files, and reset each desk to $1,000.
Verdict so far: **no edge yet** (tiny sample; 3x slippage and the 5-min 37-session check are negative for all paper desks). The +5% target is rare: since 2010 it happened on 0.17% of SPY days and 3-10% of 3x-ETF days, while the −2.5% stop level was hit on 19-31% of 3x-ETF days.
Backtests: GitHub Actions `floor-lab` after each weekday close; results `data:backtests/floor/latest/REPORT.md`. Paper books: `data:ledger/daytrade_books.json`, trades `data:ledger/daytrade_trades.csv`. Tracked daily by the Accountant (daily close) task.

### Research desk (charter `research/CHARTER.md`, set by Vivek 2026-10-26)
- The five setups: ORB + volume, EMA 9/21 + volume, Volume spike (paper since Oct 26), CVD turn and GEX verticals (to be built, back-tested once, then paper).
- **Month-1 paper test: Oct 26 to Nov 25 (23 sessions). Desk rules are frozen.** At most about 23 trades per desk, so verdicts will be "promising / inconclusive / failing" with confidence intervals; the 50-trade gate is out of reach inside the month. Month-1 report due Sat Nov 28.
- Backtests run once, when a setup is first adopted. After that: paper every day. floor-lab keeps running as the 1-minute archiver and parity replay.
- Combos (portfolio, confluence and gating, sequencing) are pre-registered in `research/combos.md` and judged on forward days only. Variant count: `research/VARIANTS.md`. Queue: `research/QUEUE.md`.

### Other setups
| Setup | Stage | Notes |
|---|---|---|
| ORB SPY/TQQQ (original Pine design) | spec | superseded on paper by the ORB + volume desk above |
| CVD turn 3-min | spec | buy from 5-candle low, sell from 5-candle high; skip spikes; RTH only |
| GEX-filtered SPY/SPX verticals | idea (spec for review) | Skylit connected = GEX data unblocked (365 days). Proposed 5-filter spec in `strategies/gex_spreads/spec.md`, waiting on Vivek's answers (8 questions). No code yet. |
| Control: SPY buy-and-hold | spec | benchmark |
| Control: 9/21 EMA cross | spec | now a real desk (EMA 9/21 + volume); SPY buy-and-hold from Oct 26 stays the benchmark |

### Crypto Pier (BTC/ETH spot, long only; spec `strategies/crypto_pier/spec.md`)
| Desk | Stage | Backtest, Robinhood costs, 2% risk (2017 to Oct 2026) |
|---|---|---|
| BTC breakout 20/10 | backtest | +17.1%/yr, max DD −21.7%, Sharpe 0.99 vs BTC hold 1.0; 3 trades made most of it |
| BTC trend 100-day | backtest | +4.9%/yr, max DD −14.5%, Sharpe 0.58 |
| ETH trend 100-day | backtest | +4.0%/yr, max DD −18.8%, Sharpe 0.48; negative since 2022 |
| ETH breakout 20/10 | backtest | flash-crash artifact (−90% DD from Coinbase's 2017 ETH crash); needs trailing exit |
| 4h EMA swing, day-trade breakout, day-trade dip-buy, RSI(2) dip-buy | retired | lose money after fees |
| Drop-bounce, momentum-burst, squeeze-breakout (short-horizon, 3-15 day; meant as a defined-risk ETF options overlay) | retired | all 3 fail the screen on both coins after Robinhood-level costs; momentum-burst is the least bad (positive expectancy, Sharpe ~0.3-0.4) but still below buy-and-hold |
Next (research queue in the spec): trailing breakout exit, close-based stops, real Robinhood spreads.

## Hustles (autonomous department from 2026-10-26; rules in `hustles/OPERATING.md`)
Claude runs the department alone: ideas, building, launching, killing, scaling. Vivek is contacted only for (1) funding for a hustle already proven at $0 cost (extreme case), (2) a one-time store and payout setup when a product is ready to sell, and (3) a notice when income is ready to move to the live fund. Scheduled task "Hustle Department" (Sonnet 5.5) runs daily at 8:43 AM PT while products are being built, and switches itself to Tue and Fri once everything is live and only waiting on sales.
| Experiment | Stage | Revenue | Notes |
|---|---|---|---|
| Trader Toolkit (spreadsheet templates + ready-made Pine indicators) | building | $0 | `hustles/templates/`; digital products, no client contact |
| Pine Script commissions (Fiverr) | dropped 2026-10-26 | $0 | needs live client chats; Fiverr requires the owner to represent his gig |
| Discord bots for clients | dropped 2026-10-26 | $0 | needs live clients, permissions and deadlines |
| Build-in-public posts (LinkedIn) | dropped 2026-10-26 | $0 | LinkedIn's terms ban automated posting |
Ledger: `hustles/LEDGER.csv` (no rows yet).

## Waiting on Vivek (City Hall)
- `ALERT_WEBHOOK_URL` in Railway (optional, for phone alerts)
- Alpha Vantage connector (not blocking)
- ~~Add `SKYLIT_API_KEY`~~ done Oct 26 22:10 PT (deploy 4202b52a): logs show `CHECK skylit spot: ok, 6/6 symbols`; the price cross-check and Yahoo fallback are on from the Oct 27 open
- Decide on Fix 3, realistic stop/target fills (`docs/proposals/2026-10-26-fix3-stop-target-model.md`)
- Update the project instructions: name Vivek, new capital rule (text in DECISIONS 2026-10-13), Crypto Pier section
- Make the GitHub repo private (it is public now)
- Let the Railway GitHub App see `trading-lab` (auto-deploy on push isn't firing; no skipped deploys, so webhooks never arrive). Workaround: Claude deploys by reconnecting the service source (connect-service-source), which builds the latest `main`.

## Plan
Claude Pro → Risk Officer runs once a day (10 AM PT), not hourly.

## Models for scheduled tasks (Vivek, 2026-10-26: Claude assigns them; don't default everything to the top model)
| Task | Model | Why |
|---|---|---|
| Researcher (quant desk), Wed + Sat 3:34 PM | Opus 5.5 | edge hunting, paper-data statistics, combos: subtle bugs (look-ahead, overfitting) cost the most |
| Accountant (daily close), weekdays 2:40 PM | Sonnet 5.5 | routine reading, arithmetic in code, records |
| Hustle Department, daily 8:43 AM | Sonnet 5.5 | building products, listings, research, records |
Rules for new and changed tasks:
- **Opus 5.5:** research and backtests, go-live reviews, independent checks before going live, and anything touching the risk engine or live-order code.
- **Sonnet 5.5:** building, writing and routine runs.
- **Haiku 5.5:** simple check-only runs (heartbeat or deploy status, with no judgment calls).
- **Fable 5.1:** not used for scheduled runs.

`create_trigger` can't pick a model (new tasks inherit the session's model), so set the model with `update_trigger` right after creating a task. A scheduled run may change its own schedule only, never its model.

## Phase 0 checklist
- [x] 1. Check connections: GitHub ok (App installed), Railway ok, folder ok, Alpha Vantage pending
- [x] 2. Repo structure, STATE.md, DECISIONS.md, risk engine + 29 unit tests (all caps block)
- [x] 3. Railway worker deployed 2026-10-13; logs: `RESULT: 5/5 connectivity checks passed` (sandbox account, SPY quote, 34 SPY expirations, clock)
- [x] 4. Adapter, shadow fills, ledger, data push live. PR #1 merged; logs: ledger restore 3 files, paper_equity 1000, live_equity 1000, 4 files pushed. Paper baseline locks at the first market-hours loop.
- [x] 5. Compound City published with SAMPLE data, checked at desktop (1366px) and phone (390px)
- [ ] 6. Scheduled residents (automatic approval, phone alert only at checkpoints):
  - "Researcher (quant desk)", Wed + Sat 3:34 PM PT, Opus 5.5 (created 2026-10-26; charter `research/CHARTER.md`). It replaces "Researcher (Floor + Pier)" (Sat 6:34 AM PT, created 2026-10-24), which still needs to be disabled or deleted by Vivek: Claude's attempt was blocked.
  - "Accountant (daily close)", weekdays 2:40 PM PT (created 2026-10-25): paper stats vs SPY, city, STATE.md, retire proposals, Friday scorecard
  - Still to do: Mayor, Newsie, Risk Officer, Hustle Scout
- [~] 7. Day-trade desks on paper from 2026-10-26; hustle one-pagers posted 2026-10-13

## How the city gets data (for residents)
- Database of the artifact above; write with ArtifactData (url = the artifact link). Docs:
  - `city/state`: `bot`, `treasury`, `watchtower`, `newsstand`, `ticker` (newest first, keep ~30), `decisions`, `sample_note` (remove once nothing is sample)
  - `agents/<id>`: residents (`mayor`, `newsie`, `risk`, `accountant`, `researcher`, `scout`), setups (`orb`, `cvd`, `gex`, `ctl-spy`, `ctl-ema`), hustles (`h-*`). Fields: name, short, kind, icon, home, district, status (working|waiting|needs_me|error|asleep), action, action_at, progress, history[≤10], queue[], links[], handoff{to,active}, sample; setups add stage, symbols, metrics{...,as_of,source,sample}, equity[{t,v%}], tradeable{live_equity,ok,why}; hustles add stage, revenue, costs, hours, one_pager
  - `cityhall/<id>`: title, kind (decision|task), status (pending|yes|no|done|later), detail, from/from_label, created_at, answered_at, sample. **Read answers here at the start of every run.**
  - `ledger/trades`: rows[≤100] {t, setup, symbol, side, qty, price, shadow_price, pnl_r, ref}
- Every number carries `as_of` and `source` (ledger file + row). Set `sample: false` when a value becomes real.
- Seed generator: `city/make_seed.py` (only for a reset; it overwrites real data).

## Known gaps (honest list)
- The repo is public: strategy code, ledger and decisions are visible to anyone. No secrets are in it.
- Crypto paper trading doesn't exist yet: Tradier has no crypto. When a Pier rule passes, crypto paper runs inside the bot on live quotes.
- Paper end-of-day exits fill about 1-2 min after 15:55 ET (Oct 26: 15:56:43) at the live price, while the backtest exits at the 15:55 bar's open. The bot acts on the 15:55 bar once it completes. Small, but paper and backtest differ here; fixing it touches engine/ (needs Vivek's yes).
- floor-lab's after-close GitHub Actions run (21:25 UTC) had not started by 21:50 UTC on Oct 26; GitHub's scheduler often runs late. Next Accountant run checks it.
- Day-trade fills use Yahoo's live last price (verified real-time vs Skylit on Oct 26; no bid/ask) + slippage. Since deploy d8f0b896 (Oct 26 17:46 PT) every fill is logged with quote time, quote age (flag > 90 s), signal-bar time, the backtest rule price next to the paper price, and a Skylit check of all six ETFs (flag > 0.05%; on since Oct 26 22:10 PT, when `SKYLIT_API_KEY` was added). If Yahoo fails, positions are valued with Skylit and no new entries open. Stops/targets still fill at the live price; a realistic model is proposed, not built. While Yahoo is down, stops/targets aren't checked (unchanged). Tradier sandbox orders are mirrors only, sandbox token only.
- GEX: Skylit gives 365 days of historical gamma and ~2 years of IV, but real intraday option prices only for the last 30 days. Older spread fills must be modeled; a real-price archive can start on Vivek's yes.
- No strategy has a validated edge yet. Controls exist so we can tell.
- Railway has no volume; /ledger and risk_state.json are restored from branch `data` at startup (fixed 2026-10-13).
- The Tradier sandbox account shows $100,000 equity and is a margin-type account. Paper orders must be sized as if live-size (rule 7), not off $100k. Decision 2026-10-13: paper runs as a virtual $1,000 account, whole shares; each setup also reports 'tradeable at $1,000 live: yes/no' (Vivek's expected real live size at go-live, not the $50 own-money cap). Risk engine already blocks margin and short entries.
