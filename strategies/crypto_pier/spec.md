# Crypto Pier — spec and status

_Owner: Vivek Gomathinayagam. Research lab code: `lab/crypto/`. Results: branch `data`, folder `backtests/crypto/latest/` (REPORT.md, results.json, equity_daily.csv, trades_main.csv)._

No `config.yaml` here on purpose: nothing on the Pier is cleared for paper or live, so the bot doesn't load it.

## What the Pier is
- BTC and ETH, **spot only, long only**. No leverage, no perpetuals or futures, no shorting (money rule 4). Meme coins are out of scope.
- Deterministic rules, decided at a bar's close, filled at the next bar's open. No LLM in the trading loop.
- Live venue when anything earns it: Robinhood (its Crypto Trading API can place orders; v2 API orders pay the taker rate, up to 0.95% per side at the entry tier). Live orders only come from the bot and only after Vivek says go live (money rules 2, 3, 9).
- Same caps as everything else: 5% max loss per trade, 10% daily stop, 30% drawdown kill switch.

## Hypotheses tested (pre-registered 2026-10-24)
| Family | Style | Why it might work | Main rule |
|---|---|---|---|
| trend_sma | swing, daily | crypto trends persist (time-series momentum) | long while close > 100-day SMA, 3×ATR trailing stop |
| trend_voltarget | swing, daily | same, with size scaled to volatility | as above, size = 40% / 30-day vol |
| donchian | swing, daily | breakouts start trends (Turtle rules) | buy close > prior 20-day high, sell close < prior 10-day low, fixed 2×ATR stop |
| rsi2_meanrev | swing, daily | short dips inside uptrends bounce | buy RSI(2) < 10 above 200-day SMA, exit close > 5-day SMA or 10 days |
| ema_cross_4h | swing, 4h | faster trend capture | long while EMA20 > EMA50 on 4h bars |
| intraday_breakout | day, 1h | intraday momentum | buy close > prior 24h high if yesterday was in an uptrend; out after 12h or stop |
| intraday_meanrev | day, 1h | intraday overreaction | buy hourly RSI(14) < 25 in a daily uptrend; out at RSI > 50 or 24h |

22 parameter variants per asset in total (7 main + 15 sensitivity). Data: Coinbase Exchange public candles, 2017-01-01 to 2026-10-23.

## First results (run 2026-10-24, Robinhood costs)
- **Day trading is dead.** Both intraday rules lose 85–90% a year after fees, and they had no real edge even before fees.
- **4h swing and RSI(2) dip-buying are dead.** The 4h rule has some edge before fees but trades 500+ times; fees erase it. RSI(2) has none.
- **Daily trend following is the only family that survives fees**, because it trades 5–11 times a year:
  - BTC 100-day trend, 2% risk: +4.9%/yr, max drawdown −14.5%, Sharpe 0.58.
  - BTC 20/10 breakout, 2% risk: +17.1%/yr, max drawdown −21.7%, Sharpe 0.99.
  - BTC buy-and-hold for comparison: +56%/yr, max drawdown −84%, Sharpe 1.0.
- **Nothing passed the screen.** None beat buy-and-hold on risk-adjusted return. The breakout's 14× total comes from 3 trades (2019, 2020–21, 2024–25); without its best 5 trades it loses money. Since 2022 both BTC trend rules grew far less than holding BTC.
- **ETH breakout's −96% drawdown is a venue artifact with a real lesson:** a February 2017 entry kept a fixed stop near $12 while ETH ran to $400; Coinbase's exchange flash-crashed to about $0.10 on 21 June 2017 and the stop filled. Deep, stale resting stops on one venue are dangerous.

## Stage
| Desk | Stage |
|---|---|
| BTC trend 100-day | backtest (refining) |
| ETH trend 100-day | backtest (refining) |
| BTC breakout 20/10 | backtest (refining) |
| ETH breakout 20/10 | backtest (refining) |
| 4h EMA swing | retired |
| Day-trade breakout | retired |
| Day-trade dip-buy | retired |
| RSI(2) dip-buy | retired |
| Drop-bounce (short-horizon mean reversion) | retired |
| Momentum-burst (short-horizon continuation) | retired |
| Squeeze-breakout (short-horizon volatility breakout) | retired |

## Crypto ETF / options overlay idea (tested 2026-10-25)
Vivek asked whether a short-term directional pattern on BTC/ETH could be traded via a crypto ETF (IBIT, FBTC, BITO, etc.) using calls/puts for defined risk instead of spot. Two honest limits on this, upfront:
- "Decades" of history doesn't exist for this instrument: usable BTC/ETH spot data runs ~2017-2026 (what the lab already uses); the ETFs themselves are new (BITO launched Oct 2021, spot ETFs like IBIT/FBTC launched Jan 2024), and listed options on them have even less history. There's no way to backtest crypto-ETF options directly over a long window.
- The approach taken: test short-horizon (3-15 day) directional patterns on the real BTC/ETH spot series the lab already has — a pattern found there is the thing a call/put would try to capture, since these ETFs track spot closely (ignoring tracking error and financing cost, which paper trading would still need to check).

Three patterns tested, pre-registered before running: **drop-bounce** (buy after a ≥10% single-day drop, hold up to 5 days — mean reversion), **momentum-burst** (buy after a ≥15% 3-day move, hold up to 5 days — continuation), **squeeze-breakout** (buy a breakout out of a volatility contraction, hold up to 10 days). 5 extra parameter variants each (16 total), same Robinhood-cost assumptions and 2017-2026 data as the rest of the Pier.

**Result: all three fail the screen on both BTC and ETH.** Drop-bounce and squeeze-breakout lose money after costs on both coins. Momentum-burst is the only one with positive expectancy after costs (profit factor 1.5-3.2 depending on cost/sizing slice) but its Sharpe (0.3 BTC, 0.4-0.5 ETH) stays below simply holding the coin, and it still fails the drawdown and out-of-sample checks. None of the three are a basis for an options trade yet — a short-dated option adds theta decay and implied-vol cost on top of a spot pattern that doesn't clear the bar on its own.

## Research queue (each item gets a written hypothesis before it is run; variant count is reported)
1. Trailing breakout exit (channel stop that ratchets up) vs the fixed Turtle stop, to remove stale far-away stops.
2. Close-based stops (bot checks at the close; no resting order on the exchange) vs intrabar stops, to measure flash-crash exposure.
3. Real Robinhood costs: measure live bid/ask spreads with read-only Robinhood crypto quotes, since default "market maker" routing prices through the spread rather than a listed fee.
4. A 2022+ hold-out is now spent; new ideas are judged on walk-forward results and on forward (live-data) paper only.
5. If momentum-burst is refined further (longer lookback, volatility filter) and clears the screen on spot, model it as a real options trade before paper: strike/expiry choice, theta cost over the hold period, and bid/ask on the actual ETF options chain — a spot pass is necessary but not sufficient for an options version to work.

## Gates (same tournament as the Trading Floor)
- Backtest screen: 30+ trades, positive expectancy after Robinhood costs, profit factor 1.2+, max drawdown no worse than −20%, Sharpe above buy-and-hold on the same coin, positive in 2 of 3 periods, positive after 2022.
- Paper: crypto paper runs inside the bot on live quotes (Tradier has no crypto). A slow rule trading ~8 times a year needs years for 30 live trades, so its paper stage checks that live signals and fills match the backtest, not trade count alone. Vivek decides; the evidence and the risk go to City Hall.
