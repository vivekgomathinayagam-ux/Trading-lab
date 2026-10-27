# Paper-trading data audit — 2026-10-26

_Requested by Vivek: confirm whether the 15-minute Tradier sandbox delay affects the paper results, per strategy, before relying on them. Read-only audit: no execution code changed, no endpoint switched, no orders sent._

## Bottom line
- **The official paper results do not use Tradier data.** Signals come from Yahoo 1-minute bars. Entry and exit prices come from Yahoo's latest trade price plus a fixed slippage. Tradier sandbox only receives mirror orders ("plumbing only"). Their delayed fills are never used in results.
- **Yahoo's price was real-time on Oct 26.** Each SPY fill matched Skylit's 1-second spot at the same second within $0.03 (see the table below). Against the price 15 minutes earlier, the gaps were $0.36–$1.55.
- **Real gaps, unrelated to the 15-minute delay:**
  1. Quote timestamps aren't recorded, so quote age can't be proven from the ledger.
  2. Paper stop and target exits would fill at the live price ~1–2 min later, not at the stop/target level the backtest uses (no stop or target has triggered yet).
  3. EOD exits fill at ~15:56:43, while the backtest uses the 15:55 bar's open.
  4. Yahoo is an unofficial source: no bid/ask, robots.txt disallows automated access, and it can rate-limit or break without notice.
- **Paper sample so far: 1 day (Oct 26), 3 trades**, all closed at end of day. The Oct 1–23 numbers in STATE are **backtests** on historical Yahoo 1-minute bars. A live-quote delay can't affect historical bars.

## Per strategy
| | ORB + volume (`orb_vol`) | EMA 9/21 + volume (`ema_vol`) | Volume spike (`volspike`) | SPY buy-and-hold (benchmark) |
|---|---|---|---|---|
| Signal data | Yahoo 1-min bars, completed bars only (`engine/marketdata.py`) | same; 5-min EMA buckets built from Yahoo 1-min bars | same | none (not a trading strategy) |
| Entry/exit price | Yahoo `regularMarketPrice` × (1 ± slippage: 0.02% SPY/QQQ, 0.05% 3x ETFs) (`engine/daytrade_runner.py`) | same | same | first Yahoo SPY price of the paper start day (762.35, Oct 26) vs latest Yahoo mark |
| Tradier sandbox use | mirror paper order only, delayed ~15 min per Tradier's sandbox docs; not used for results | same | same | none |
| Timestamps | bot clock at fill (`entry_t`, `exit_t`, ledger `ts`). **Not recorded:** Yahoo quote time (`regularMarketTime`) or the bar time that triggered the signal | same | same | benchmark has date only |
| Instruments | ETF shares only: SPY, QQQ, TQQQ, UPRO, SQQQ, SPXU (long only) | same | same | SPY shares (virtual) |

Notes:
- The EMA desk is **9/21**, not 9/12 (pre-registered 2026-10-25 in `strategies/daytrade/spec.md`).
- The older registry setups (`orb`, `controls`, `spy_buy_hold`, `cvd_turn`) are at stage `spec`, so they don't run.
- The old `engine/shadow.py` option path (delayed sandbox option quotes) is unused. No running setup trades options.

## Independent price check (Skylit `heat_historical_heatmap`, 1-second resolution)
| Fill (Oct 26, ET) | Yahoo price used (before slippage) | Skylit spot, same second | Skylit spot 15 min earlier |
|---|---|---|---|
| orb_vol SPY entry 10:11:43 | 764.318 | 764.30 | 763.42 |
| volspike SPY entry 10:53:43 | 766.680 | 766.70 | 765.135 |
| EOD SPY exits 15:56:43 | 765.140 | 765.11 | 765.50 |
| SPY mark 15:59:43 | 765.185 | 765.215 (15:59:42) | — |

The SQQQ entry wasn't checked (no Skylit call at that second). It uses the same Yahoo code path. Railway logs for Oct 26 show no feed failures and no "skipped stale signal" lines.

## Real-time sources checked
| Source | Real-time? | Bars + volume for signals? | Bid/ask? | Cost | Limits / risks |
|---|---|---|---|---|---|
| **Yahoo chart API (current)** | yes for these ETFs (verified above) | yes, 1-min OHLCV | no | free | unofficial, no SLA, robots.txt disallows automated access, can rate-limit; 1-min history only ~30 days |
| **Skylit** (`heat_heatmap` / `heat_levels` spot) | yes, 1-second snapshots; covers all six ETFs (checked) | **no**: Skylit's stock series has no stock OHLC or stock volume (per the `regime` skill's data notes), so it can't drive the volume-spike signals | no | 1 credit per call for up to 10 symbols; a check at each fill ≈ 6 credits/day (negligible). Polling every minute ≈ 390 credits/day ≈ $0.39/day | spot methodology (last trade vs mid) undocumented; Skylit plan cost isn't tracked in the Treasury yet |
| **Tradier production API** | yes for account holders | yes | yes | needs a production token | the token can trade; putting it in Railway breaks money rule 3 (bot holds only the sandbox token). **Not recommended** without Vivek's explicit decision |
| Alpha Vantage | real-time US data needs a paid plan (per their docs; price not verified here) | yes | no | paid | connector not connected |
| Alpaca free (IEX feed) | real-time, but one exchange only | yes | yes | free with an account | IEX volume is a small slice of the market, so volume-spike signals would change. Needs a new account (Vivek) |

## Recommended fix (proposal only — needs Vivek's yes before any code change)
The feed is already real-time. The simplest safe fix makes that **provable** and closes the backtest/paper gaps. Executions stay simulated.
1. **Record provenance on every fill and mark:** Yahoo `regularMarketTime`, the signal bar's start time, the bot time, the computed `quote_age_s`, and the feed name. Flag any fill with quote age > 90 s. _(Ledger fields only, no trading change.)_
2. **Independent cross-check at each fill:** one Skylit `heat_levels` call (all six symbols in one call, 1 credit). Log Skylit spot and the % difference. Flag differences > 0.05%. ~6 credits/day.
3. **Exit at the rule's level, like the backtest:** a stop or target exit fills at the stop/target price, or the bar's open if price gapped through. Today it fills at the live price. _This changes paper fill logic, so it waits for Vivek's yes._
4. **EOD exit at the 15:55 bar's open**, or record both prices. Already listed as a known gap; same approval.
5. **Fallback:** if Yahoo fails, mark positions with Skylit spot but take no new entries (Skylit has no volume for signals). Log every fallback.
6. Keep Tradier sandbox mirror orders as plumbing tests, labeled "not used for results". No production endpoint.

Data cost: ≈ 6–12 Skylit credits a day (≈$0.01). No new accounts, no secrets, no live token.

## What to do with results so far
**Retain them, labeled. Don't discard or re-run.**
- The 3 paper trades from Oct 26 used real-time Yahoo prices. The three SPY fills were independently checked against Skylit.
- Label: "Yahoo real-time last trade + assumed slippage; no bid/ask; quote time not recorded (SPY fills verified against Skylit on 2026-10-26)."
- They're EOD exits, so the exit-level gap (#3) didn't affect them. The EOD timing gap (#4) did, slightly (15:56:43 live price vs 15:55 bar open).
- The Oct 1–23 backtests stand as backtests.
- Nothing either way is meaningful yet: 3 trades is far from the 50-trade gate.
