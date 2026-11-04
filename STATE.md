# STATE.md — Compound City

_Read this first. Updated by every session and scheduled task. Times are America/Los_Angeles._

**Read next: `research/LESSONS.md` (what we know), `research/BOARD.md` (agent-to-agent items), `research/IDEAS.md` (test backlog).**

**Interactive 2026-11-03 13:00 PT:**
- Vivek's review led to a restructure: daily post-mortems, a new Session Coach resident, an autonomous Researcher, and shared LESSONS/BOARD/IDEAS files.
- Crypto Pier is retired.
- Foundry batch 1 tested 6 trend/Fibonacci rules on 2 samples: all refuted (`research/foundry/batch1_REPORT.md`).
- Waiting on Vivek: an Alpaca data key, and one bundled yes for the 4 paper-engine fixes.

**Researcher as of 2026-11-04 17:00 PT (Wed build run):**
- Batch 2 and condor study 1, 5 tests, all pre-registered (`research/foundry/batch2_REPORT.md`):
  - giveback trail: refuted (desk entries +0.0015%/trade, CI [−0.05, +0.05]; worse than holding on random entries)
  - 10:30 trend-day gate: refuted
  - reversal day: refuted
  - 1-day SPY iron condor at ±1 sigma: refuted (21 trades, −$12.52 per condor; 81% wins, but 4 breaches erased them; max loss ~$450, over the 5% cap at $1k)
  - no entries from 13:00 ET: weakly supported (LESSONS 23), forward-tested on the paper ledger
- No desk added or retired: nothing passed, and no desk has 20+ paper trades. Variants 156. Skylit 424 credits (balance 104,533).

**Researcher (previous) as of 2026-10-31 16:30 PT:** Saturday review: no desk has an edge (2-5 trades each); parity 10/16; Oct 30 Yahoo froze at 14:44 ET and volspike's SPXU exit used a 74-min-old price (+$24.10 logged, ~+$9.27 real) -> PR #2 awaiting Vivek; Skylit pilot 2: no intraday GEX effect, variance premium in Tempest. Note `research/weekly/2026-W44.md`.
**As of:** 2026-11-04 17:00 PT (Researcher build run; see above). Accountant: 2026-11-04 14:45 PT (daily close, paper day 8: 6 trades, 2 wins (CVD TQQQ +$4.07, CVD SPY +$0.68), 4 small eod losses (EMA and EMA v2 QQQ -$5.63 each, ORB UPRO -$6.28, Vol spike UPRO -$1.84); no +5% hits; bot healthy, kill switch off; SPY hold +0.54% since start)
**Previously:** 2026-11-03 14:50 PT (daily close, paper day 7: 6 trades, 1 win (CVD TQQQ +$2.98), 5 small losses; EMA v2 took its first paper trade; no +5% hits; bot healthy, kill switch off; SPY hold −1.02% since start)
**Earlier:** 2026-11-02 14:45 PT (daily close, paper day 6: 4 trades, all losses)
**Hustles as of 2026-11-04 08:50 PT:** no sales data reachable; ledger unchanged; new free risk-of-ruin table page published to repo.

## Phase
Phase 0 — building from zero. See the Phase 0 checklist below.

## What runs where
| Thing | Where | Status |
|---|---|---|
| Bot (worker) | Railway, project `compound-city` (6e2d45ea), service `bot` (94c0bd23), env `production`, region us-east4 | **running**; deploys from `main` |
| Code | GitHub `vivekgomathinayagam-ux/Trading-lab`, branch `main` | pushed |
| Ledger snapshots | branch `data`, folder `ledger/` | first push 2026-10-13 21:10 UTC |
| Crypto Pier lab | GitHub Actions `crypto-lab` (manual only since 2026-11-03) | **retired** 2026-11-03: nothing passed in 4 runs |
| Foundry lab + post-mortem | GitHub Actions `foundry-lab` (weekdays 22:05 UTC, on lab/foundry changes, manual) | results `data:backtests/foundry/latest/`, post-mortems `data:research/postmortem/`, 5-min archive `data:backtests/data/etf5m/` |
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
| ORB + volume | **paper from 2026-10-26** | 12 trades, −2.65%, PF 0.55, +5% hits 0 | 6 trades (1 win), −1.96%, PF 0.03, vs SPY −2.50 pts; Nov 4: UPRO −$6.28 (eod) (as of Nov 4 close) | 09:30-09:45 range breakout on a volume-spike bar |
| EMA 9/21 + volume | **paper from 2026-10-26** | 11 trades, −2.51%, PF 0.33, +5% hits 0 | 6 trades (0 wins), −2.06%, PF 0, vs SPY −2.60 pts; Nov 4: QQQ −$5.63 (eod) (as of Nov 4 close) | 5-min EMA cross with a 1-min volume spike in that bucket |
| Volume spike | **paper from 2026-10-26** | 17 trades, +1.13%, PF 1.2, +5% hits 0 | 8 trades (3 wins), +2.15%, PF 1.97, vs SPY +1.61 pts; Nov 4: UPRO −$1.84 (eod). Includes the Oct 30 SPXU +$24.10 logged on a frozen quote (~+$9.27 real); ledger not edited (as of Nov 4 close) | spike bar closes up, above VWAP and the prior 15-bar high |
| EMA 9/21 + volume v2 (`ema_vol_v2`) | **paper from 2026-10-29** | 14 trades, −0.43%, PF 0.82 (Oct 1-27; reference only, design touched by paper data) | 2 trades (0 wins), −0.58%, $994.19, vs SPY −1.12 pts; Nov 4: QQQ −$5.63 (eod) (as of Nov 4 close) | bug-fix version: 5-min buckets by clock (Yahoo drops 1-6% of UPRO/SPXU minutes, which merged buckets in `ema_vol`) |
| CVD turn SPY (`cvd_spy`) | **paper from 2026-10-29** | 19 trades, −0.12%, PF 0.90, expectancy −0.006%/trade [−0.07, +0.06] | 5 trades (2 wins), −0.10%, PF 0.70, vs SPY −0.64 pts; Nov 4: SPY +$0.68 (as of Nov 4 close) | Vivek's setup; spec `strategies/cvd_turn/spec.md`; CVD approximated from 1-min bars (close location) |
| CVD turn TQQQ (`cvd_tqqq`) | **paper from 2026-10-29** | 19 trades, +9.3%, PF 10.4, +0.47%/trade [+0.19, +0.78]; 2x costs +0.37%; 3x +0.28% | 5 trades (4 wins), +0.63%, PF 1.36, vs SPY +0.09 pts; Nov 4: TQQQ +$4.07 (as of Nov 4 close) | best of 6 symbols tried (QQQ +0.07, UPRO 0.00, SQQQ −0.27, SPXU −0.08 per trade): treat as suspect until paper agrees; all exits on the CVD sell turn, holds 3-33 min |
| ORB plain / EMA plain / Volume spike 2x | backtest only | +0.37% / +0.46% / +0.28% | — | comparisons |
| SPY buy-and-hold | benchmark | −0.58% same window | +0.54% (762.35 → 766.435, as of Nov 4 close) | control |
**Evaluation status (Vivek, 2026-10-26):** Oct 26 trades are labeled `preliminary` (Yahoo real-time + assumed slippage, no quote time recorded). A fresh evaluation starts once the new logging is verified in a live session: every fill in `ledger/daytrade_fills.csv` has quote time, age, bar time, and a Skylit cross-check within 0.05% (needs `SKYLIT_API_KEY`). Then: set `evaluation:` in `strategies/daytrade/config.yaml` to `eval-1`, archive the preliminary ledger files, and reset each desk to $1,000.
Verdict so far: **no edge yet** (tiny sample; 3x slippage and the 5-min 37-session check are negative for all paper desks). The +5% target is rare: since 2010 it happened on 0.17% of SPY days and 3-10% of 3x-ETF days, while the −2.5% stop level was hit on 19-31% of 3x-ETF days.
Backtests: GitHub Actions `floor-lab` after each weekday close; results `data:backtests/floor/latest/REPORT.md`. Paper books: `data:ledger/daytrade_books.json`, trades `data:ledger/daytrade_trades.csv`. Tracked daily by the Accountant (daily close) task.

### Research desk (charter `research/CHARTER.md`, set by Vivek 2026-10-26)
- **Entry-quality study (2026-10-29, Vivek's request):** `research/entries/REPORT.md`. 1,094 signals, 28 features, chronological train/val/test. No filter or score beat the desks out-of-sample (0 of 90 configs passed). Held in both halves: extended entries and low-ATR conditions do worse (shadow-test candidates H1/H2). cvd_tqqq's result is its first signal of the day (+0.46% vs -0.07% for later signals). Bug found: `CVDTurn.signal()` doesn't check the symbol (paper, no bad trade yet; fix needs Vivek's yes). Nothing changed.
- **Exit study (2026-10-29, Vivek's request; entries frozen):** `research/exits/REPORT.md`. 89 trades, 18 exit variants: fixed take-profits worse than baseline; ATR trail best in-sample but failed walk-forward (+0.06 vs +0.19%/trade); 3:55 PM flat protects (holding overnight -0.30% vs +0.05%). **Nothing changed.** Proposed: paper clones `cvd_tqqq_atr2`, `cvd_spy_atr3`; re-run at about 40 sessions.
- The five setups: ORB + volume, EMA 9/21 + volume, Volume spike (paper since Oct 26), CVD turn and GEX verticals (to be built, back-tested once, then paper).
- **Month-1 paper test: Oct 26 to Nov 25 (23 sessions). Desk rules are frozen.** At most about 23 trades per desk, so verdicts will be "promising / inconclusive / failing" with confidence intervals; the 50-trade gate is out of reach inside the month. Month-1 report due Sat Nov 28.
- Backtests run once, when a setup is first adopted. After that: paper every day. floor-lab keeps running as the 1-minute archiver and parity replay.
- **Saturday review 2026-10-31** (`research/weekly/2026-W44.md`): 16 trades, every desk too small to say; parity 10/16 (1 stale-feed bug, 2 ema_vol buckets, 3 likely Yahoo bar revisions); Skylit pilot 2: 0DTE board has no 60-90 min effect; Tempest: realized next-day move ~0.7x priced (variance premium, both halves) -> next: real-price iron condor study. Combo C-2 registered. Variants 138.
- Paper report `lab/floor/paper_report.py` and parity replay `lab/floor/replay.py` exist (2026-10-28). Parity Oct 26-27: 4/5 trades match; 1 explained (`research/parity/2026-10-28.md`).
- **Foundry batch 1 (2026-11-03):** 6 rules, each long and short: Ripster cloud ride ×2, VWAP trend, trend break, Fib 61.8, Fib 38.2. Tested on 26 sessions of 1-min and 41 of 5-min. All refuted (`research/foundry/batch1_REPORT.md`). Next: a trend-day gate (BOARD).
- **Foundry batch 2 + condor study 1 (2026-11-04):** giveback trail, trend-day gate, reversal day, 1-day ±1σ iron condor: all refuted. 13:00 ET entry cutoff: tentative, forward test on the paper ledger (wrong if 10 late paper entries average ≥ 0). foundry-lab now runs batch 2 each weekday. Next Wed: prior-day high/low and opening-drive rules (`research/QUEUE.md`).
- Combos (portfolio, confluence and gating, sequencing) are pre-registered in `research/combos.md` and judged on forward days only. Variant count: `research/VARIANTS.md`. Queue: `research/QUEUE.md`.

### Other setups
| Setup | Stage | Notes |
|---|---|---|
| ORB SPY/TQQQ (original Pine design) | spec | superseded on paper by the ORB + volume desk above |
| CVD turn 3-min | **paper from 2026-10-29** as `cvd_spy` and `cvd_tqqq` (see the day-trade table) | |
| GEX / Skylit setups | research | The Researcher's own project (charter). Pilot 2 (2026-10-31): 0DTE boards at 10:00/12:30 ET show no magnet, regime or accelerant effect over 60-90 min; Tempest shows a variance premium (next-day move ~0.7x priced). Pilot 1 (2026-10-28, 62 days of 10:00 ET boards, SPY/QQQ): no king pull, no gamma-sign effect on the rest-of-day move. Next: intraday horizon, 0DTE-only boards, Tempest IV. Log: `research/skylit/STUDY.md`. |
| Control: SPY buy-and-hold | spec | benchmark |
| Control: 9/21 EMA cross | spec | now a real desk (EMA 9/21 + volume); SPY buy-and-hold from Oct 26 stays the benchmark |

### Crypto Pier: RETIRED 2026-11-03 (kept for reference; spec `strategies/crypto_pier/spec.md`)
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
| Trader Toolkit (journal + risk calculator spreadsheets) | **LIVE** (2026-10-27, $12) | $0 | `hustles/templates/`; two tested .xlsx files + listing in `product/`. Store: vivekgo8.gumroad.com/l/aobhdm. Promotion plan in `hustles/templates/promo/PLAN.md`. Pine pack held back: can't be compile-tested without TradingView. Oct 28: free cheat sheet + calculator pages, Plan Pack workbook (tested, not yet in store), community drafts queued for Chrome |
| Funded-Account Drawdown Tracker (prop-firm rule tracker, $9) | **building** (2026-10-29) | $0 | `hustles/propdd/`; workbook built and recalculated, listing + explainer written; publishing queued for a Chrome session |
| Pine Script commissions (Fiverr) | dropped 2026-10-26 | $0 | needs live client chats; Fiverr requires the owner to represent his gig |
| Discord bots for clients | dropped 2026-10-26 | $0 | needs live clients, permissions and deadlines |
| Build-in-public posts (LinkedIn) | dropped 2026-10-26 | $0 | LinkedIn's terms ban automated posting |
Ledger: `hustles/LEDGER.csv` (no rows yet). Nov 2 run: $0 known revenue, day 7 of 45; no sales data reachable; new page options-breakeven-with-fees.md. Prior, Nov 1 run: $0 known revenue, day 6 of 45; no sales data reachable; new page daily-loss-limit-and-pre-trade-checklist.md. Prior, Oct 31 run: $0 known revenue, day 5 of 45 for the Toolkit; no sales data reachable; new page r-multiple-expectancy-explained.md. Prior, Oct 30 run: $0 known revenue, day 4 of 45 for the Toolkit; no sales data reachable; new page vertical-spread-max-loss-calculator.md. Prior note: Hustle table as of 2026-10-29 09:10 PT (Oct 29 run: no sales data reachable; second experiment built). Trader Toolkit: $0 revenue, 0 known sales (day 2 of 45); sales data not reachable from cloud runs, so a sale will show up when Vivek's Gumroad email is seen or an interactive session checks the dashboard.

## Waiting on Vivek (City Hall)
- ~~Trader Toolkit store setup~~ done Oct 27; product published
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
| Session Coach (daily post-mortem), weekdays 6:13 PM | Sonnet 5.5 | reads the scripted post-mortem, writes one lesson, board items (created 2026-11-03, trig_011Fgio2UtAqRaH7jRgSBsvE) |
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
- Accountant 2026-11-03: floor-lab's 21:25 UTC run had not appeared by 22:40 UTC (latest REPORT generated 2026-11-03 02:58 UTC, the Nov 2 session). Paper figures come from the bot's ledger and are unaffected. Also `ledger/risk_state.json` shows start-of-day paper equity 1006.97 / peak 1056.64, which does not match the desk-book average at start of day (999.46); the Watchtower drawdown (4.7%) comes from it. Not investigated (engine/ untouched).
- Accountant 2026-11-02: floor-lab's 21:25 UTC run had not appeared by 22:40 UTC; latest REPORT is still the run generated 2026-10-31 00:53 UTC (Oct 30 session). Paper figures come from the bot's ledger and are unaffected. PR #2 (stale-quote fix) still unmerged, d-stalefeed pending at City Hall.
- **Researcher 2026-10-31, cause found:** Yahoo froze for all six ETFs at 14:44 ET on Oct 30 (quote 4,416 s old at the exit; Skylit 36.035 vs Yahoo 36.565). No 15:55 bar arrived, so only the 15:58 safety exit fired, at the frozen price: volspike's +$24.10 is really about +$9.27 (book +$21.86, not +$36.71). The ledger is not edited. Fix: PR #2 (stale quote > 300 s = feed down -> Skylit valuation, entries paused), unmerged, needs Vivek's yes. Earlier note follows.
- Accountant 2026-10-30: Volume spike's SPXU exit today was reason `eod_safety` at 15:58:10 ET, not the usual `eod` at about 15:56 (every earlier EOD exit was 15:56). The safety net worked and the position was flat, but the regular 15:55 exit did not fire for this one. Not investigated (engine/ untouched); worth a look by the Researcher or Vivek. Also: floor-lab's Oct 30 21:25 UTC run had not appeared by 21:45 UTC (latest REPORT is the 2026-10-30 01:09 UTC run); paper figures come from the bot's ledger and are unaffected.
- Skylit price check flags every fill (max diff over all six ETFs > 0.05%) because SPXU (−0.12% to −0.23%) and SQQQ (−0.11% to −0.07%) disagree with Yahoo; the traded symbol's diff was within 0.07% (TQQQ −0.007% and +0.063% on Oct 27). The flag is driven by the untraded inverse ETFs, so it may be too noisy to be useful. Logged by the Accountant 2026-10-27; engine/ untouched.
- Accountant 2026-10-29: floor-lab's latest results are from the run at 2026-10-29 01:03 UTC (Oct 28 session); today's 21:25 UTC run had not appeared by 21:41 UTC (GitHub scheduler lateness again). Paper figures come from the bot's own ledger, so they are unaffected.
- floor-lab's earlier results were from the run at 2026-10-28 00:34 UTC (Oct 27 session); today's 21:25 UTC run had not appeared at 21:41 UTC (GitHub schedules often run late). Logged by the Accountant 2026-10-28.
- The repo is public: strategy code, ledger and decisions are visible to anyone. No secrets are in it.
- Crypto paper trading doesn't exist yet: Tradier has no crypto. When a Pier rule passes, crypto paper runs inside the bot on live quotes.
- Paper end-of-day exits fill about 1-2 min after 15:55 ET (Oct 26: 15:56:43) at the live price, while the backtest exits at the 15:55 bar's open. The bot acts on the 15:55 bar once it completes. Small, but paper and backtest differ here; fixing it touches engine/ (needs Vivek's yes).
- floor-lab's after-close GitHub Actions run (21:25 UTC) had not started by 21:50 UTC on Oct 26; GitHub's scheduler often runs late. Next Accountant run checks it.
- Day-trade fills use Yahoo's live last price (verified real-time vs Skylit on Oct 26; no bid/ask) + slippage. Since deploy d8f0b896 (Oct 26 17:46 PT) every fill is logged with quote time, quote age (flag > 90 s), signal-bar time, the backtest rule price next to the paper price, and a Skylit check of all six ETFs (flag > 0.05%; on since Oct 26 22:10 PT, when `SKYLIT_API_KEY` was added). If Yahoo fails, positions are valued with Skylit and no new entries open. Stops/targets still fill at the live price; a realistic model is proposed, not built. While Yahoo is down, stops/targets aren't checked (unchanged). Tradier sandbox orders are mirrors only, sandbox token only.
- GEX: Skylit gives 365 days of historical gamma and ~2 years of IV, but real intraday option prices only for the last 30 days. Older spread fills must be modeled; a real-price archive can start on Vivek's yes.
- No strategy has a validated edge yet. Controls exist so we can tell.
- Railway has no volume; /ledger and risk_state.json are restored from branch `data` at startup (fixed 2026-10-13).
- The Tradier sandbox account shows $100,000 equity and is a margin-type account. Paper orders must be sized as if live-size (rule 7), not off $100k. Decision 2026-10-13: paper runs as a virtual $1,000 account, whole shares; each setup also reports 'tradeable at $1,000 live: yes/no' (Vivek's expected real live size at go-live, not the $50 own-money cap). Risk engine already blocks margin and short entries.
