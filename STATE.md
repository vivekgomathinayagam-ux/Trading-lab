# STATE.md — Compound City

_Read this first. Updated by every session and scheduled task. Times are America/Los_Angeles._

**As of:** 2026-10-24 17:30 PT (Phase 0, step 5 done; Crypto Pier lab added and first BTC/ETH backtests run)

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
| Setup | Stage | Notes |
|---|---|---|
| ORB SPY/TQQQ | spec | Vivek's design; Pine signal + Python backtest |
| CVD turn 3-min | spec | buy from 5-candle low, sell from 5-candle high; skip spikes; RTH only |
| GEX-filtered SPY/SPX verticals | idea | needs GEX source (FlashAlpha) and real options history to backtest |
| Control: SPY buy-and-hold | spec | benchmark |
| Control: 9/21 EMA cross | spec | benchmark |

### Crypto Pier (BTC/ETH spot, long only; spec `strategies/crypto_pier/spec.md`)
| Desk | Stage | Backtest, Robinhood costs, 2% risk (2017 to Oct 2026) |
|---|---|---|
| BTC breakout 20/10 | backtest | +17.1%/yr, max DD −21.7%, Sharpe 0.99 vs BTC hold 1.0; 3 trades made most of it |
| BTC trend 100-day | backtest | +4.9%/yr, max DD −14.5%, Sharpe 0.58 |
| ETH trend 100-day | backtest | +4.0%/yr, max DD −18.8%, Sharpe 0.48; negative since 2022 |
| ETH breakout 20/10 | backtest | flash-crash artifact (−90% DD from Coinbase's 2017 ETH crash); needs trailing exit |
| 4h EMA swing, day-trade breakout, day-trade dip-buy, RSI(2) dip-buy | retired | lose money after fees |
Next (research queue in the spec): trailing breakout exit, close-based stops, real Robinhood spreads.

## Hustles (all proposed 2026-10-13; waiting on Vivek at City Hall)
| Hustle | One-pager | 90-day range | Autonomy |
|---|---|---|---|
| Trader spreadsheet templates (Gumroad/Etsy) | `hustles/templates/one-pager.md` | $0-150 | high |
| Pine Script commissions (Fiverr) | `hustles/pine/one-pager.md` | $0-300 | **approved Oct 21**; Vivek wants Claude to run the store; setup pending |
| Discord bots for trading communities (Fiverr) | `hustles/discord/one-pager.md` | $0-450 | medium |
| Build-in-public posts (LinkedIn/Medium) | `hustles/buildlog/one-pager.md` | $0-25 direct; resume value | high |
Not recommended now: local-business tools (needs heavy outreach), print-on-demand, surveys or microtasks (often ban AI help), anything selling trading signals.

## Waiting on Vivek (City Hall)
- `ALERT_WEBHOOK_URL` in Railway (optional, for phone alerts)
- Alpha Vantage connector (not blocking)
- 3 hustle decisions (templates, Discord bots, build log); Pine approved Oct 21
- How the Fiverr store gets run (see DECISIONS 2026-10-21)
- Update the project instructions: name Vivek, new capital rule (text in DECISIONS 2026-10-13), Crypto Pier section
- Make the GitHub repo private (it is public now)
- Let the Railway GitHub App see `trading-lab` (auto-deploy on push isn't firing; no skipped deploys, so webhooks never arrive). Workaround: Claude deploys by reconnecting the service source (connect-service-source), which builds the latest `main`.

## Plan
Claude Pro → Risk Officer runs once a day (10 AM PT), not hourly.

## Phase 0 checklist
- [x] 1. Check connections: GitHub ok (App installed), Railway ok, folder ok, Alpha Vantage pending
- [x] 2. Repo structure, STATE.md, DECISIONS.md, risk engine + 29 unit tests (all caps block)
- [x] 3. Railway worker deployed 2026-10-13; logs: `RESULT: 5/5 connectivity checks passed` (sandbox account, SPY quote, 34 SPY expirations, clock)
- [x] 4. Adapter, shadow fills, ledger, data push live. PR #1 merged; logs: ledger restore 3 files, paper_equity 1000, live_equity 1000, 4 files pushed. Paper baseline locks at the first market-hours loop.
- [x] 5. Compound City published with SAMPLE data, checked at desktop (1366px) and phone (390px)
- [ ] 6. Scheduled residents: "Researcher (Floor + Pier)" runs Saturdays 6:34 AM PT (created 2026-10-24, automatic approval, phone alert only at checkpoints). Mayor, Newsie, Risk Officer, Accountant and Hustle Scout still to do.
- [ ] 7. Start setups; first Hustle Scout one-pagers

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
- Shadow fills use Yahoo's 1-minute last price (no bid/ask) + 2 bps slippage. Options shadow fills use delayed sandbox quotes. Real-time options need a paid feed.
- GEX setup cannot be backtested honestly without historical options data (paid). Forward paper test only until funded.
- No strategy has a validated edge yet. Controls exist so we can tell.
- Railway has no volume; /ledger and risk_state.json are restored from branch `data` at startup (fixed 2026-10-13).
- The Tradier sandbox account shows $100,000 equity and is a margin-type account. Paper orders must be sized as if live-size (rule 7), not off $100k. Decision 2026-10-13: paper runs as a virtual $1,000 account, whole shares; each setup also reports 'tradeable at $1,000 live: yes/no' (Vivek's expected real live size at go-live, not the $50 own-money cap). Risk engine already blocks margin and short entries.
