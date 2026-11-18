# News & momentum stock scalper (`news_scalp`): spec v1, 2026-11-17

Source: Vivek's brief (2026-11-17, "AI-Powered News & Momentum Stock Scalping Agent"). Stage: **research** (Mode 1). Paper only after the backtest gate; live mode not built.

## Rules (from the brief)
- US stocks, long only, one position at a time, max $1,000 notional, whole shares, no leverage, never overnight.
- 1 trade a day; a 2nd only with score ≥ 90, a fresh catalyst and the first trade closed. Max 2 round trips.
- Hold ≤ 120 s from the first fill; exit at target, stop, setup invalid, or 120 s.
- Risk engine (independent of the signal): planned loss ≤ $5/trade, daily realized loss ≤ $7.50 then stop, no averaging down. (Inside the project cap: 5% of $1,000 = $50.)
- Liquidity: price > $5, ADV > $25M, spread ≤ 0.10%, no OTC, halts or tiny floats.
- Windows: 09:40-11:30 ET primary; 14:00-15:30 ET tested separately.
- Setups: A news momentum pullback (VWAP/EMA9 reclaim); B 5-min ORB with confirmation.
- Score 0-100 (catalyst 20, liquidity 20, trend 20, RVOL 15, entry 15, market/RS 10); ≥ 80 to trade. Calibrated against results, not a probability.
- Targets 0.30-0.60%, stops 0.20-0.35% (grid; never tightened to qualify). Net P&L after spread, slippage and fees.

## Data (probe 2026-11-17, `lab/news/probe_alpaca.py`, one Alpaca key)
| Need | Source | Status |
|---|---|---|
| Universe / discovery | Alpaca screener movers + most-actives | works |
| News, live | Alpaca News (Benzinga) REST + websocket | works (latest 50) |
| News, history | Alpaca News | returned 0 for a 2024 window: recheck params (symbols, sort) |
| Filings | SEC EDGAR (free) | to add |
| Tick history for 120 s backtests | Alpaca SIP trades + quotes | works (AAPL 2 min = 10,000 trades) |
| Real-time quotes | Alpaca IEX feed | works; recent SIP needs a paid plan. IEX is a partial book: spreads and fills must be checked against it |
| Paper orders | Alpaca paper account | active |
| Catalyst reading | Claude in a pre-market scheduled run (no LLM in the trading loop) + deterministic intraday keyword/category scorer | to build |

## Architecture (reuse what exists)
- Scanner, news agent, technicals, scoring: new `lab/news/` (research) then `strategies/news_scalp/` (paper).
- Pre-market: a scheduled Claude run ("Newsie", ~6:00 AM PT) reads overnight news + filings for the movers list, writes `data:news/watchlist/<day>.json` with catalyst summaries and scores. Intraday the bot only adds deterministic scores for fresh headlines.
- Risk: reuse `engine/risk` with a news_scalp profile (the $5 / $7.50 limits sit inside the project caps). Changing engine/risk needs Vivek's yes.
- Execution: an Alpaca paper broker adapter (marketable-limit, cancel if price runs, fill reconciliation, restart-safe). This is engine/brokers: needs Vivek's yes. Railway also needs ALPACA_KEY_ID / ALPACA_SECRET_KEY (Vivek types them).
- Reporting: daily report per section 15 of the brief, read by the Session Coach.

## Backtest gate (before paper)
- Replay historical news + SIP trades/quotes; entries at the ask, exits at the bid, latency ≥ 1 s; no fill on a touch.
- Chronological train / validation / holdout (holdout = 2026); walk-forward; count every variant.
- Pass: positive net expectancy with CI above 0 on the holdout, PF ≥ 1.2, both setups judged separately, ≥ 200 historical trades.
- Wrong if: net expectancy ≤ 0 after costs on the holdout, or the edge is all spread capture that IEX quotes can't reproduce.

## Honest prior
At a 120 s hold, a 0.05-0.10% spread plus slippage eats a third to half of a 0.30% target. Most published news-scalping edges vanish after realistic fills. The backtest decides.


## v1 scope (Vivek, 2026-11-17 evening): the goal restated
Develop a strategy that can **confidently call a small % move, up or down**, by combining every resource we have: news, macro/political events, charts and price action, volume, Skylit options flow, and Claude's reasoning. Open to any liquid ticker, not a fixed list.

**Universe (any of these, filtered by the liquidity rules above):** US stocks with fresh catalysts; ADRs and country ETFs (EWZ, FXI, EWJ, EWW, INDA, KWEB...) when foreign political or economic news hits; sector ETFs (XLE, XLF, SMH...) for macro news; index ETFs and their inverse versions.

**Direction:** up = buy the stock/ETF. Down = buy an inverse ETF (SQQQ, SPXU, SOXS...) or a defined-risk long put. No shorting (needs margin, money rule 4).

**Inputs and what each is for**
| Input | Role | Source |
|---|---|---|
| Company news, filings | catalyst: what moved and why | Alpaca News (Benzinga), SEC EDGAR, Alpha Vantage news sentiment |
| Macro and political news | which countries, sectors, rates or currencies are hit | pre-market web search by Claude, economic calendar (CPI, FOMC, jobs, tariffs, elections) |
| Charts and price action | timing and confirmation: trend, VWAP, key levels, gaps, opening range | Alpaca 1-min/5-min bars |
| Volume | the one signal working on our desks so far (volspike): relative volume and spikes confirm the move is real | Alpaca bars |
| Options flow | confirmation of conviction (sweeps, flow tide) | Skylit (inside the study budget) |
| Claude reasoning | reads the news, judges surprise vs. expected, picks tickers, writes the watchlist with a direction and a confidence | pre-market scheduled run only (no LLM in the trading loop) |

**How "confident" gets measured (not claimed):** every call is logged before the open: ticker, direction, size of move, window, confidence 0-100. A scorer checks it against what the price actually did. Confidence buckets must be calibrated (calls marked 80 should be right about 80% of the time) and beat a no-skill baseline before any desk trades on them.

**Two tracks, run together**
1. **Forward call log (starts now, costs nothing):** a pre-market run writes `news/calls/<day>.json`; the lab scores it after the close. This builds the track record that historical news data may not give us.
2. **Historical event study:** once the Alpaca news history query works, replay catalysts against 1-min bars to find which kinds of news (earnings surprise, guidance, FDA, macro print, tariff headline...) lead to follow-through vs. fade, and which chart/volume conditions sharpen it.

A paper desk starts only when one track clears the backtest gate above (or the forward log reaches 50+ calls with calibrated, above-baseline accuracy after costs).
