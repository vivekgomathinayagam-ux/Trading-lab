# STATE.md — Compound City

_Read this first. Updated by every session and scheduled task. Times are America/Los_Angeles._

**As of:** 2026-10-09 (Phase 0, first session)

## Phase
Phase 0 — building from zero. See the Phase 0 checklist below.

## What runs where
| Thing | Where | Status |
|---|---|---|
| Bot (worker) | Railway, project `compound-city` (6e2d45ea), service `bot` (94c0bd23), env `production` | created, no source yet |
| Code | GitHub `vivekgomathinayagam-ux/Trading-lab`, branch `main` | first commit |
| Ledger snapshots | branch `data`, folder `ledger/` | not yet pushed |
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
- Link GitHub to Claude (so the repo can be pushed)
- Type `TRADIER_SANDBOX_TOKEN` into Railway Variables
- Alpha Vantage connector (not blocking)
- Claude plan tier (decides Risk Officer cadence)

## Phase 0 checklist
- [x] 1. Check connections (GitHub blocked on linking; Railway ok; folder ok; Alpha Vantage pending)
- [x] 2. Repo structure, STATE.md, DECISIONS.md, risk engine + 22 unit tests (all caps block)
- [ ] 3. Railway project + worker; first deploy with Tradier connectivity check; logs confirmed
- [ ] 4. Tradier adapter, shadow-fill simulator, ledger writer, data-branch push — code written, deploy + log confirmation pending
- [ ] 5. Compound City artifact with SAMPLE data, desktop + phone
- [ ] 6. Scheduled residents
- [ ] 7. Start setups; first Hustle Scout one-pagers

## Known gaps (honest list)
- Shadow fills use Yahoo's 1-minute last price (no bid/ask) + 2 bps slippage. Options shadow fills use delayed sandbox quotes. Real-time options need a paid feed.
- GEX setup cannot be backtested honestly without historical options data (paid). Forward paper test only until funded.
- No strategy has a validated edge yet. Controls exist so we can tell.
