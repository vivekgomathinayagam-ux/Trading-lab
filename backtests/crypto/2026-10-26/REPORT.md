# Crypto Pier — historical backtest report

_Generated 2026-10-26 03:31 UTC from Coinbase Exchange public candles (1h, 1d). Data 2017-01-01 to 2026-10-25._

## How to read this

- Long-only spot BTC and ETH. No leverage, no shorting.
- Signals at a bar's close, fills at the next bar's open plus 0.05% slippage; stops fill at the stop or worse on a gap.
- **Headline = Robinhood costs (0.95% fee per side, its entry-tier taker rate for API orders) with 5%-risk sizing** (a stop hit loses at most ~5% of equity, money rule 5). 2%-risk sizing is shown too: same rules, smaller bets, smaller drawdowns.
- 'mid' assumes a 0.40% fee (cheaper exchange, assumption). 'gross' = slippage only, to see if any edge exists before fees.
- Parameters were fixed before running. 30 parameter variants per asset were run in total (10 pre-registered + 20 sensitivity). Results from many variants overstate edge; the walk-forward table shows how picking the best backtest actually held up.
- The 'pattern' family (drop_bounce, momentum_burst, squeeze_breakout) are short-horizon (3-15 day) setups meant to map to a defined-risk long call/put on a crypto ETF, not the spot position actually simulated here. They do not model options theta, implied vol, or ETF tracking error — a pass here is a reason to size a real options trade carefully in paper, not evidence the options trade itself works.

## Data quality

| Asset | Timeframe | Bars | Missing | Largest 1-bar move | Flash-crash wicks (low < half the bar's body) |
|---|---|---|---|---|---|
| BTC-USD | 1h | 85987 | 0.06% | 22.0% | none |
| BTC-USD | 1d | 3584 | 0.0% | 38.8% | 2017-04-15 |
| ETH-USD | 1h | 86002 | 0.04% | 19.6% | 2017-06-21 |
| ETH-USD | 1d | 3584 | 0.0% | 43.3% | 2017-06-21 |

A flash-crash wick on one exchange can trigger a resting stop far below the real market (ETH on Coinbase's exchange, 21 June 2017, traded near $0.10 for a moment). The engine fills such stops at the stop price, as a real stop order on that venue could have, so these bars can cause large one-day losses. 'Worst day' in the screen shows it.

## Benchmarks (buy and hold, no costs after entry)

| Asset | CAGR | Max DD | Sharpe |
|---|---|---|---|
| BTC-USD | 56.3% | -83.8% | 1.0 |
| ETH-USD | 77.7% | -94.0% | 1.08 |
| Cash | 0% | 0% | 0 |

## Headline: Robinhood fees, 5%-risk sizing (the rule maximum)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 108 | 26.9% | 1.15% | 1.67 | 10.2% | -31.4% | 0.57 | 53.0% | 182.7% | 20.8% | 3.6% | 7.5% | 0.23 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 108 | 26.9% | 1.15% | 1.67 | 10.2% | -31.4% | 0.57 | 53.0% | 182.7% | 20.8% | 3.6% | 7.5% | 0.23 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 9.261% | 4.06 | 30.9% | -38.7% | 0.99 | 41.8% | 610.4% | 27.9% | 57.1% | 15.5% | 0.31 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 82 | 51.2% | -0.546% | 0.42 | -4.7% | -37.8% | -0.67 | 7.4% | 48.4% | -3.6% | -3.3% | -6.6% | -0.71 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.958% | 0.63 | -46.5% | -99.9% | -1.27 | 52.6% | 291.8% | -20.4% | -52.1% | -57.3% | -2.26 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.85% | 0.11 | -88.4% | -100.0% | -7.52 | 7.4% | 98.3% | -87.8% | -87.4% | -89.6% | -8.05 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -2.012% | 0.17 | -42.3% | -99.6% | -2.8 | 3.2% | 96.8% | -39.4% | -47.9% | -39.9% | -3.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -1.606% | 0.46 | -5.3% | -52.8% | -0.5 | 2.8% | 19.6% | -8.3% | -9.7% | 0.9% | -0.45 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 0.796% | 1.71 | 2.6% | -14.3% | 0.33 | 4.4% | 38.5% | 7.0% | -0.8% | 1.8% | 0.07 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.516% | 0.82 | -6.8% | -73.7% | -0.25 | 14.5% | 166.8% | 16.2% | -9.9% | -19.6% | -1.26 |
| ETH-USD | trend_sma(n=100) | swing | 117 | 25.6% | 0.891% | 1.53 | 8.6% | -41.5% | 0.49 | 52.9% | 141.3% | 17.1% | 9.2% | 1.9% | -0.07 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 117 | 25.6% | 0.889% | 1.53 | 8.6% | -41.5% | 0.49 | 52.9% | 141.1% | 17.0% | 9.2% | 1.9% | -0.07 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 5.187% | 2.66 | 18.2% | -96.0% | 0.87 | 38.8% | 256.5% | -1.7% | 75.1% | 0.3% | 0.0 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 79 | 54.4% | -0.502% | 0.47 | -4.1% | -36.5% | -0.61 | 7.3% | 35.6% | -3.9% | -2.1% | -5.9% | -0.85 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.445% | 0.83 | -32.5% | -99.5% | -0.55 | 50.7% | 684.1% | -0.8% | -20.1% | -56.5% | -1.71 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.77% | 0.18 | -85.8% | -100.0% | -6.32 | 7.2% | 219.9% | -79.1% | -90.4% | -85.7% | -6.67 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -2.139% | 0.24 | -47.8% | -99.8% | -2.3 | 3.2% | 116.4% | -41.9% | -57.6% | -43.5% | -2.73 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.56% | 0.74 | -4.3% | -52.5% | -0.32 | 7.0% | 39.0% | -1.4% | -10.6% | -1.4% | -0.64 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 48.1% | 0.791% | 1.48 | 5.2% | -32.8% | 0.43 | 9.7% | 78.9% | 12.7% | -4.1% | 7.2% | 0.5 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.469% | 1.18 | 1.6% | -34.1% | 0.18 | 12.9% | 139.3% | 8.5% | -2.9% | -0.1% | -0.03 |

## Robinhood fees, 2%-risk sizing (same rules, smaller bets)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 108 | 26.9% | 0.475% | 1.7 | 4.8% | -14.5% | 0.57 | 53.0% | 47.9% | 8.9% | 2.0% | 4.0% | 0.26 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 108 | 26.9% | 0.475% | 1.7 | 4.8% | -14.5% | 0.57 | 53.0% | 47.9% | 8.9% | 2.0% | 4.0% | 0.26 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 4.035% | 4.15 | 17.0% | -21.7% | 0.99 | 41.8% | 99.5% | 15.0% | 31.3% | 8.5% | 0.39 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 82 | 51.2% | -0.218% | 0.42 | -1.8% | -16.9% | -0.68 | 7.4% | 22.1% | -1.4% | -1.3% | -2.6% | -0.72 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.426% | 0.67 | -23.6% | -94.7% | -1.05 | 52.6% | 255.1% | -4.3% | -24.9% | -35.1% | -1.88 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.78% | 0.1 | -87.4% | -100.0% | -7.66 | 7.4% | 99.8% | -85.5% | -86.1% | -89.5% | -8.07 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -1.835% | 0.12 | -39.2% | -99.2% | -2.92 | 3.2% | 88.7% | -34.9% | -43.0% | -39.4% | -3.08 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -0.663% | 0.46 | -2.1% | -26.0% | -0.51 | 2.8% | 9.1% | -3.3% | -3.9% | 0.4% | -0.46 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 0.318% | 1.7 | 1.1% | -5.9% | 0.32 | 4.4% | 13.9% | 2.9% | -0.3% | 0.7% | 0.06 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.095% | 0.92 | -1.4% | -41.2% | -0.1 | 14.5% | 77.2% | 10.6% | -2.7% | -9.1% | -1.25 |
| ETH-USD | trend_sma(n=100) | swing | 117 | 25.6% | 0.356% | 1.53 | 3.9% | -18.8% | 0.47 | 52.9% | 38.0% | 7.3% | 4.2% | 1.2% | -0.07 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 117 | 25.6% | 0.356% | 1.53 | 3.9% | -18.8% | 0.47 | 52.9% | 38.0% | 7.3% | 4.2% | 1.2% | -0.07 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 2.083% | 2.66 | 9.2% | -89.7% | 0.64 | 38.8% | 49.0% | 0.3% | 31.7% | 0.7% | -0.01 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 79 | 54.4% | -0.201% | 0.47 | -1.6% | -16.3% | -0.61 | 7.3% | 15.9% | -1.5% | -0.8% | -2.3% | -0.86 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.096% | 0.92 | -9.0% | -82.0% | -0.28 | 50.7% | 382.5% | 6.3% | -2.5% | -23.8% | -1.15 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.651% | 0.17 | -83.7% | -100.0% | -6.52 | 7.2% | 200.8% | -73.9% | -88.5% | -85.2% | -6.66 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -1.71% | 0.19 | -40.1% | -99.4% | -2.5 | 3.2% | 99.2% | -35.0% | -42.5% | -41.9% | -2.72 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.224% | 0.74 | -1.6% | -24.8% | -0.31 | 7.0% | 16.4% | -0.2% | -4.3% | -0.5% | -0.65 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 48.1% | 0.317% | 1.48 | 2.4% | -14.1% | 0.44 | 9.7% | 26.2% | 5.6% | -1.4% | 2.9% | 0.5 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.252% | 1.23 | 1.7% | -15.3% | 0.23 | 12.9% | 52.3% | 3.8% | 0.2% | 1.3% | 0.06 |

## Same rules at a 0.40% fee (assumed cheaper exchange), 5%-risk sizing

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 108 | 29.6% | 1.604% | 2.14 | 15.7% | -28.4% | 0.82 | 53.0% | 102.0% | 24.9% | 7.9% | 15.0% | 0.54 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 108 | 29.6% | 1.604% | 2.14 | 15.7% | -28.4% | 0.82 | 53.0% | 102.0% | 24.9% | 7.9% | 15.0% | 0.54 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 43.4% | 10.116% | 4.86 | 36.3% | -35.8% | 1.12 | 41.8% | 337.5% | 32.3% | 62.8% | 21.4% | 0.53 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 82 | 64.6% | -0.122% | 0.84 | -1.2% | -17.8% | -0.15 | 7.4% | 24.1% | -2.0% | -1.1% | -0.6% | -0.04 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 27.7% | -0.012% | 0.99 | -9.0% | -90.0% | -0.06 | 52.6% | 547.8% | 26.0% | -21.2% | -21.0% | -0.87 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 22.3% | -0.765% | 0.35 | -59.2% | -100.0% | -4.08 | 7.4% | 106.2% | -54.9% | -60.1% | -61.6% | -5.1 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 33.7% | -0.945% | 0.43 | -23.0% | -92.5% | -1.73 | 3.2% | 78.1% | -20.8% | -29.9% | -19.1% | -2.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -1.142% | 0.58 | -3.9% | -47.8% | -0.37 | 2.8% | 8.8% | -6.0% | -7.8% | 1.0% | -0.33 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 67.6% | 1.354% | 2.5 | 4.5% | -9.9% | 0.56 | 4.4% | 17.9% | 10.2% | 0.8% | 3.2% | 0.28 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 39.4% | 0.393% | 1.17 | 1.6% | -55.4% | 0.18 | 14.5% | 104.2% | 25.2% | -1.6% | -11.5% | -0.75 |
| ETH-USD | trend_sma(n=100) | swing | 117 | 26.5% | 1.24% | 1.86 | 13.1% | -30.4% | 0.69 | 52.9% | 74.3% | 20.1% | 13.3% | 7.8% | 0.21 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 117 | 26.5% | 1.238% | 1.86 | 13.1% | -30.4% | 0.69 | 52.9% | 74.1% | 20.1% | 13.3% | 7.8% | 0.21 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 41.5% | 5.907% | 3.15 | 22.5% | -95.9% | 0.94 | 38.8% | 136.2% | 1.6% | 79.8% | 5.1% | 0.17 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 79 | 63.3% | -0.188% | 0.77 | -1.7% | -24.6% | -0.23 | 7.3% | 16.9% | -2.4% | 0.0% | -2.4% | -0.44 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 29.3% | 0.379% | 1.18 | 4.9% | -87.2% | 0.33 | 50.7% | 1374.8% | 44.6% | 19.3% | -26.5% | -0.68 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 27.5% | -0.688% | 0.48 | -53.8% | -100.0% | -2.97 | 7.2% | 265.5% | -37.6% | -63.5% | -56.1% | -3.72 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 33.4% | -1.089% | 0.48 | -28.7% | -97.1% | -1.43 | 3.2% | 89.8% | -20.0% | -40.8% | -24.6% | -1.94 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 53.1% | -0.181% | 0.91 | -1.9% | -40.5% | -0.11 | 7.0% | 18.4% | 2.8% | -8.0% | -0.5% | -0.48 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 55.7% | 1.208% | 1.82 | 8.8% | -24.2% | 0.67 | 9.7% | 39.2% | 17.2% | 0.6% | 9.1% | 0.7 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 42.4% | 1.213% | 1.54 | 8.3% | -30.3% | 0.48 | 12.9% | 82.1% | 14.7% | 4.2% | 6.7% | 0.3 |

## Before fees (slippage only), 5%-risk sizing

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 108 | 32.4% | 1.938% | 2.61 | 19.9% | -26.2% | 1.0 | 53.0% | 0.0% | 27.9% | 11.2% | 20.8% | 0.77 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 108 | 32.4% | 1.938% | 2.61 | 19.9% | -26.2% | 1.0 | 53.0% | 0.0% | 27.9% | 11.2% | 20.8% | 0.77 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 43.4% | 10.743% | 5.61 | 40.4% | -33.6% | 1.22 | 41.8% | 0.0% | 35.6% | 67.2% | 25.8% | 0.68 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 82 | 73.2% | 0.189% | 1.29 | 1.4% | -14.3% | 0.25 | 7.4% | 0.0% | -0.9% | 0.5% | 4.0% | 0.5 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 34.2% | 0.683% | 1.49 | 34.1% | -50.3% | 0.99 | 52.6% | 0.0% | 76.2% | 13.2% | 23.7% | 0.41 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 36.8% | 0.032% | 1.05 | 1.9% | -41.6% | 0.19 | 7.4% | 0.0% | 16.6% | -7.5% | -1.2% | -0.2 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 39.1% | -0.161% | 0.86 | -5.1% | -57.4% | -0.36 | 3.2% | 0.0% | -3.7% | -13.0% | 0.4% | -0.42 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -0.802% | 0.68 | -2.9% | -43.9% | -0.26 | 2.8% | 0.0% | -4.2% | -6.5% | 1.2% | -0.23 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 73.5% | 1.764% | 3.22 | 6.0% | -8.9% | 0.72 | 4.4% | 0.0% | 12.6% | 1.9% | 4.2% | 0.44 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 43.6% | 1.06% | 1.53 | 8.3% | -39.4% | 0.51 | 14.5% | 0.0% | 32.1% | 4.9% | -5.1% | -0.33 |
| ETH-USD | trend_sma(n=100) | swing | 117 | 27.4% | 1.497% | 2.18 | 16.6% | -26.9% | 0.83 | 52.9% | 0.0% | 22.4% | 16.4% | 12.3% | 0.41 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 117 | 27.4% | 1.495% | 2.18 | 16.5% | -26.9% | 0.83 | 52.9% | 0.0% | 22.4% | 16.4% | 12.3% | 0.41 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 45.3% | 6.435% | 3.59 | 25.8% | -95.8% | 0.99 | 38.8% | 0.0% | 4.0% | 83.3% | 8.7% | 0.29 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 79 | 65.8% | 0.041% | 1.06 | 0.2% | -17.8% | 0.06 | 7.3% | 0.0% | -1.3% | 1.7% | 0.2% | -0.12 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 34.0% | 0.983% | 1.59 | 44.7% | -54.7% | 1.04 | 50.7% | 0.0% | 90.4% | 59.7% | 7.6% | 0.19 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 39.5% | 0.107% | 1.14 | 9.0% | -66.8% | 0.47 | 7.2% | 0.0% | 38.5% | -3.5% | -0.7% | -0.13 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 38.0% | -0.319% | 0.8 | -10.5% | -79.1% | -0.47 | 3.2% | 0.0% | 1.0% | -24.4% | -7.0% | -0.77 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 53.1% | 0.097% | 1.05 | -0.1% | -29.9% | 0.05 | 7.0% | 0.0% | 5.9% | -6.1% | 0.2% | -0.37 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 58.2% | 1.513% | 2.12 | 11.4% | -18.9% | 0.85 | 9.7% | 0.0% | 20.5% | 4.2% | 10.4% | 0.85 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 49.4% | 1.759% | 1.9 | 13.4% | -27.3% | 0.72 | 12.9% | 0.0% | 19.4% | 9.7% | 11.8% | 0.56 |

## Robinhood fees, full sizing (ignores the 5% rule; for comparison)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 108 | 26.9% | 3.109% | 1.64 | 15.7% | -75.1% | 0.54 | 53.0% | 849.1% | 45.1% | 6.4% | 3.4% | 0.04 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 108 | 26.9% | 2.157% | 1.69 | 15.6% | -48.6% | 0.59 | 53.0% | 572.8% | 42.8% | 5.3% | 5.4% | 0.11 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 11.643% | 3.45 | 37.6% | -57.6% | 0.94 | 41.8% | 1447.2% | 51.6% | 57.1% | 14.9% | 0.16 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 82 | 51.2% | -1.107% | 0.57 | -10.6% | -70.0% | -0.37 | 7.4% | 94.8% | -11.4% | -10.9% | -9.8% | -0.47 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.982% | 0.68 | -50.3% | -100.0% | -1.03 | 52.6% | 398.2% | -21.6% | -60.3% | -58.4% | -2.24 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.853% | 0.11 | -88.4% | -100.0% | -7.51 | 7.4% | 98.3% | -87.9% | -87.5% | -89.6% | -8.05 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -1.963% | 0.21 | -41.8% | -99.5% | -2.68 | 3.2% | 107.0% | -38.1% | -47.6% | -39.9% | -3.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 32 | 43.8% | -3.847% | 0.48 | -14.6% | -86.3% | -0.5 | 3.0% | 32.9% | -26.3% | -21.1% | 1.9% | -0.46 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 2.377% | 1.99 | 7.1% | -30.0% | 0.42 | 4.4% | 113.6% | 25.5% | -3.8% | 3.0% | -0.05 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.674% | 0.82 | -9.5% | -79.2% | -0.25 | 14.5% | 184.6% | 12.2% | -12.8% | -21.2% | -1.32 |
| ETH-USD | trend_sma(n=100) | swing | 117 | 25.6% | 3.328% | 1.5 | 6.9% | -91.4% | 0.45 | 52.9% | 653.0% | 35.1% | -3.9% | -3.3% | -0.18 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 117 | 25.6% | 1.31% | 1.41 | 8.7% | -68.9% | 0.41 | 52.9% | 290.1% | 19.4% | 10.3% | -0.3% | -0.12 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 9.68% | 2.88 | 27.9% | -97.1% | 0.98 | 38.8% | 1054.1% | 0.8% | 140.8% | -6.3% | -0.09 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 79 | 54.4% | -1.456% | 0.59 | -14.2% | -82.0% | -0.34 | 7.3% | 80.4% | -17.2% | -12.5% | -13.0% | -0.75 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.513% | 0.87 | -46.8% | -100.0% | -0.44 | 50.7% | 581.6% | -30.2% | -36.0% | -63.0% | -1.79 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.782% | 0.18 | -86.0% | -100.0% | -6.26 | 7.2% | 216.8% | -80.0% | -90.5% | -85.7% | -6.67 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -2.1% | 0.3 | -47.8% | -99.9% | -2.03 | 3.2% | 149.7% | -38.7% | -59.9% | -43.5% | -2.73 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.418% | 0.93 | -9.2% | -84.1% | -0.07 | 7.0% | 115.3% | -2.7% | -23.4% | -1.8% | -0.51 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 80 | 47.5% | 1.885% | 1.38 | 4.5% | -77.9% | 0.31 | 9.9% | 283.1% | 22.4% | -16.8% | 10.5% | 0.19 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.595% | 1.15 | -0.1% | -54.6% | 0.16 | 12.9% | 231.8% | 19.0% | -12.3% | -3.5% | -0.13 |

## Screen for paper trading (Robinhood costs; 5% and 2% risk sizing)

Pass = 30+ trades, positive expectancy after costs, profit factor 1.2+, max drawdown no worse than -20%, Sharpe above the same asset's buy-and-hold, positive in 2 of 3 periods, positive Sharpe in 2022+.

| Asset | Strategy | Sizing | Result | Why | Worst day | Approx. breakeven fee per side |
|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | risk5 | fail | max drawdown -31.4% worse than -20%; Sharpe 0.57 not above buy-and-hold 1.0 | -9.3% | 2.429% |
| BTC-USD | trend_sma(n=100) | risk2 | fail | Sharpe 0.57 not above buy-and-hold 1.0 | -4.5% | 2.475% |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | risk5 | fail | max drawdown -31.4% worse than -20%; Sharpe 0.57 not above buy-and-hold 1.0 | -9.3% | 2.429% |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | risk2 | fail | Sharpe 0.57 not above buy-and-hold 1.0 | -4.5% | 2.475% |
| BTC-USD | donchian(entry_n=20,exit_n=10) | risk5 | fail | max drawdown -38.7% worse than -20%; Sharpe 0.99 not above buy-and-hold 1.0 | -12.7% | 7.899% |
| BTC-USD | donchian(entry_n=20,exit_n=10) | risk2 | fail | max drawdown -21.7% worse than -20%; Sharpe 0.99 not above buy-and-hold 1.0 | -8.4% | 7.859% |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.42 < 1.2; max drawdown -37.8% worse than -20%; Sharpe -0.67 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.7% | 0.243% |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.42 < 1.2; Sharpe -0.68 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -2.7% | 0.245% |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.63 < 1.2; max drawdown -99.9% worse than -20%; Sharpe -1.27 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.8% | 0.395% |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.67 < 1.2; max drawdown -94.7% worse than -20%; Sharpe -1.05 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.6% | 0.487% |
| BTC-USD | intraday_breakout(look=24,hold=12) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.11 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -7.52 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -16.6% | 0.016% |
| BTC-USD | intraday_breakout(look=24,hold=12) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.1 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -7.66 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.2% | 0.029% |
| BTC-USD | intraday_meanrev(buy_below=25) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.17 < 1.2; max drawdown -99.6% worse than -20%; Sharpe -2.8 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -12.5% | 0.0% |
| BTC-USD | intraday_meanrev(buy_below=25) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.12 < 1.2; max drawdown -99.2% worse than -20%; Sharpe -2.92 not above buy-and-hold 1.0; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.8% | 0.0% |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; max drawdown -52.8% worse than -20%; Sharpe -0.5 not above buy-and-hold 1.0; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.2% | 0.0% |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; max drawdown -26.0% worse than -20%; Sharpe -0.51 not above buy-and-hold 1.0; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -2.9% | 0.0% |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk5 | fail | Sharpe 0.33 not above buy-and-hold 1.0 | -5.8% | 1.778% |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk2 | fail | Sharpe 0.32 not above buy-and-hold 1.0 | -2.3% | 1.774% |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.82 < 1.2; max drawdown -73.7% worse than -20%; Sharpe -0.25 not above buy-and-hold 1.0; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.641% |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.92 < 1.2; max drawdown -41.2% worse than -20%; Sharpe -0.1 not above buy-and-hold 1.0; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -3.7% | 0.826% |
| ETH-USD | trend_sma(n=100) | risk5 | fail | max drawdown -41.5% worse than -20%; Sharpe 0.49 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -13.2% | 2.438% |
| ETH-USD | trend_sma(n=100) | risk2 | fail | Sharpe 0.47 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -6.6% | 2.435% |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | risk5 | fail | max drawdown -41.5% worse than -20%; Sharpe 0.49 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -13.2% | 2.435% |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | risk2 | fail | Sharpe 0.47 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -6.6% | 2.435% |
| ETH-USD | donchian(entry_n=20,exit_n=10) | risk5 | fail | max drawdown -96.0% worse than -20%; Sharpe 0.87 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -95.0% | 5.371% |
| ETH-USD | donchian(entry_n=20,exit_n=10) | risk2 | fail | max drawdown -89.7% worse than -20%; Sharpe 0.64 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -88.1% | 5.383% |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.47 < 1.2; max drawdown -36.5% worse than -20%; Sharpe -0.61 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.071% |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.47 < 1.2; Sharpe -0.61 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -2.7% | 0.074% |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.83 < 1.2; max drawdown -99.5% worse than -20%; Sharpe -0.55 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -16.1% | 0.656% |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.92 < 1.2; max drawdown -82.0% worse than -20%; Sharpe -0.28 not above buy-and-hold 1.08; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.816% |
| ETH-USD | intraday_breakout(look=24,hold=12) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.18 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -6.32 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.9% | 0.054% |
| ETH-USD | intraday_breakout(look=24,hold=12) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.17 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -6.52 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -9.8% | 0.053% |
| ETH-USD | intraday_meanrev(buy_below=25) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.24 < 1.2; max drawdown -99.8% worse than -20%; Sharpe -2.3 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -21.5% | 0.0% |
| ETH-USD | intraday_meanrev(buy_below=25) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.19 < 1.2; max drawdown -99.4% worse than -20%; Sharpe -2.5 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -17.0% | 0.0% |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.74 < 1.2; max drawdown -52.5% worse than -20%; Sharpe -0.32 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -5.9% | 0.139% |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.74 < 1.2; max drawdown -24.8% worse than -20%; Sharpe -0.31 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -2.4% | 0.14% |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk5 | fail | max drawdown -32.8% worse than -20%; Sharpe 0.43 not above buy-and-hold 1.08 | -6.8% | 2.056% |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk2 | fail | Sharpe 0.44 not above buy-and-hold 1.08 | -2.7% | 2.058% |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk5 | fail | profit factor 1.18 < 1.2; max drawdown -34.1% worse than -20%; Sharpe 0.18 not above buy-and-hold 1.08; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.6% | 1.317% |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk2 | fail | Sharpe 0.23 not above buy-and-hold 1.08 | -2.9% | 1.426% |

## Walk-forward check: pick the best variant on 2017-2021, then test 2022+

| Asset | Family | Picked on train | Train Sharpe | Test Sharpe | Test CAGR | Pre-registered main, test Sharpe | Variants compared |
|---|---|---|---|---|---|---|---|
| BTC-USD | donchian | donchian(entry_n=20,exit_n=10) | 1.44 | 0.31 | 4.7% | 0.31 | 3 |
| BTC-USD | drop_bounce | drop_bounce(drop_pct=15.0,hold=7) | 0.13 | -0.56 | -1.2% | -0.45 | 3 |
| BTC-USD | ema_cross_4h | ema_cross_4h(fast=50,slow=200) | -0.21 | -1.67 | -50.8% | -2.26 | 3 |
| BTC-USD | intraday_breakout | intraday_breakout(look=48,hold=24) | -5.43 | -5.5 | -68.7% | -8.05 | 3 |
| BTC-USD | intraday_meanrev | intraday_meanrev(buy_below=20) | -1.75 | -1.75 | -16.1% | -3.06 | 3 |
| BTC-USD | momentum_burst | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | 0.49 | 0.07 | 0.2% | 0.07 | 3 |
| BTC-USD | rsi2_meanrev | rsi2_meanrev(buy_below=5,trend_n=200) | -0.49 | -0.38 | -2.1% | -0.71 | 3 |
| BTC-USD | squeeze_breakout | squeeze_breakout(squeeze_n=30,breakout_n=20,hold=15) | 1.0 | -0.09 | -2.5% | -1.26 | 2 |
| BTC-USD | trend_sma | trend_sma(n=50) | 1.0 | 0.44 | 7.2% | 0.23 | 4 |
| BTC-USD | trend_voltarget | trend_voltarget(n=100,vol=0.3) | 0.88 | 0.23 | 2.7% | 0.23 | 3 |
| ETH-USD | donchian | donchian(entry_n=20,exit_n=10) | 1.29 | 0.0 | -3.1% | 0.0 | 3 |
| ETH-USD | drop_bounce | drop_bounce(drop_pct=15.0,hold=7) | -0.12 | -0.17 | -0.6% | -0.64 | 3 |
| ETH-USD | ema_cross_4h | ema_cross_4h(fast=50,slow=200) | 0.55 | -1.3 | -47.6% | -1.71 | 3 |
| ETH-USD | intraday_breakout | intraday_breakout(look=48,hold=24) | -4.89 | -4.86 | -69.1% | -6.67 | 3 |
| ETH-USD | intraday_meanrev | intraday_meanrev(buy_below=20) | -1.61 | -1.49 | -17.5% | -2.73 | 3 |
| ETH-USD | momentum_burst | momentum_burst(lookback=5,thresh_pct=20.0,hold=7) | 0.69 | 0.54 | 3.6% | 0.5 | 3 |
| ETH-USD | rsi2_meanrev | rsi2_meanrev(buy_below=5,trend_n=200) | -0.32 | -0.24 | -1.4% | -0.85 | 3 |
| ETH-USD | squeeze_breakout | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | 0.34 | -0.03 | -2.3% | -0.03 | 2 |
| ETH-USD | trend_sma | trend_sma(n=50) | 1.08 | 0.29 | 3.6% | -0.07 | 4 |
| ETH-USD | trend_voltarget | trend_voltarget(n=100,vol=0.4) | 0.93 | -0.07 | -3.0% | -0.07 | 3 |

## Caveats

- One exchange's history (Coinbase). Real fills on Robinhood can differ; paper trading measures that.
- Daily and 4h strategies can gap through stops overnight-style in crypto's 24/7 market; 'worst trade' shows the real damage.
- Sharpe uses daily returns x sqrt(365). Cash earns 0% here; stablecoin yield would help flat periods slightly.
- A backtest pass is a reason to paper trade, not to trade live.
