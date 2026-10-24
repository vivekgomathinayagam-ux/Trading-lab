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

## Research queue (each item gets a written hypothesis before it is run; variant count is reported)
1. Trailing breakout exit (channel stop that ratchets up) vs the fixed Turtle stop, to remove stale far-away stops.
2. Close-based stops (bot checks at the close; no resting order on the exchange) vs intrabar stops, to measure flash-crash exposure.
3. Real Robinhood costs: measure live bid/ask spreads with read-only Robinhood crypto quotes, since default "market maker" routing prices through the spread rather than a listed fee.
4. A 2022+ hold-out is now spent; new ideas are judged on walk-forward results and on forward (live-data) paper only.

## Gates (same tournament as the Trading Floor)
- Backtest screen: 30+ trades, positive expectancy after Robinhood costs, profit factor 1.2+, max drawdown no worse than −20%, Sharpe above buy-and-hold on the same coin, positive in 2 of 3 periods, positive after 2022.
- Paper: crypto paper runs inside the bot on live quotes (Tradier has no crypto). A slow rule trading ~8 times a year needs years for 30 live trades, so its paper stage checks that live signals and fills match the backtest, not trade count alone. Vivek decides; the evidence and the risk go to City Hall.
