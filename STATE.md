# STATE.md — Compound City

_Read this first. Updated by every session and scheduled task. Times are America/Los_Angeles._

**As of:** 2026-10-13 14:15 PT (Phase 0, step 3 done)

## Phase
Phase 0 — building from zero. See the Phase 0 checklist below.

## What runs where
| Thing | Where | Status |
|---|---|---|
| Bot (worker) | Railway, project `compound-city` (6e2d45ea), service `bot` (94c0bd23), env `production`, region us-east4 | **running**; deploys from `main` |
| Code | GitHub `vivekgomathinayagam-ux/Trading-lab`, branch `main` | pushed |
| Ledger snapshots | branch `data`, folder `ledger/` | first push 2026-10-13 21:10 UTC |
| City (visual) | Claude artifact "Compound City" | not built yet |
| Desk | folder "Compound City" on Gomes's Mac (iCloud) | connected, empty |

## Mode
**paper** (Tradier sandbox). Live impossible: no live token in Railway.

## Treasury
Seed: $50 (own money, cap; not yet deposited anywhere). Hustle income: $0. Trading P&L: $0.
Known monthly costs: Claude plan (tier TBC), Railway Hobby $5 (+usage).

## Setups (the tournament)
| Setup | Stage | Notes |
|---|---|---|
| ORB SPY/TQQQ | spec | Gomes's design; Pine signal + Python backtest |
| CVD turn 3-min | spec | buy from 5-candle low, sell from 5-candle high; skip spikes; RTH only |
| GEX-filtered SPY/SPX verticals | idea | needs GEX source (FlashAlpha) and real options history to backtest |
| Control: SPY buy-and-hold | spec | benchmark |
| Control: 9/21 EMA cross | spec | benchmark |

## Hustles
None proposed yet.

## Waiting on Gomes (City Hall)
- Merge PR: virtual $1,000 paper account + ledger restore + sticky kill switch (rule 9)
- `ALERT_WEBHOOK_URL` in Railway (optional, for phone alerts)
- Alpha Vantage connector (not blocking)

## Plan
Claude Pro → Risk Officer runs once a day (10 AM PT), not hourly.

## Phase 0 checklist
- [x] 1. Check connections: GitHub ok (App installed), Railway ok, folder ok, Alpha Vantage pending
- [x] 2. Repo structure, STATE.md, DECISIONS.md, risk engine + 29 unit tests (all caps block)
- [x] 3. Railway worker deployed 2026-10-13; logs: `RESULT: 5/5 connectivity checks passed` (sandbox account VA37036603, SPY quote, 34 SPY expirations, clock)
- [ ] 4. Adapter, shadow fills, ledger, data push: live in logs (branch `data` created, 3 files pushed). Open: ledger restore on restart, virtual paper equity
- [ ] 5. Compound City artifact with SAMPLE data, desktop + phone
- [ ] 6. Scheduled residents
- [ ] 7. Start setups; first Hustle Scout one-pagers

## Known gaps (honest list)
- Shadow fills use Yahoo's 1-minute last price (no bid/ask) + 2 bps slippage. Options shadow fills use delayed sandbox quotes. Real-time options need a paid feed.
- GEX setup cannot be backtested honestly without historical options data (paid). Forward paper test only until funded.
- No strategy has a validated edge yet. Controls exist so we can tell.
- 3. Railway has no volume: the container's /ledger resets on every redeploy. Fix in progress: restore /ledger from branch `data` at startup.
- 4. The Tradier sandbox account shows $100,000 equity and is a margin-type account. Paper orders must be sized as if live-size (rule 7), not off $100k. Decision 2026-10-13: paper runs as a virtual $1,000 account, whole shares; each setup also reports 'tradeable at $50 live: yes/no'. Risk engine already blocks margin and short entries.
