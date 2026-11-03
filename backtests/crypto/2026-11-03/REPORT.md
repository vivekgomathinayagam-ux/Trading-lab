# Crypto Pier — historical backtest report

_Generated 2026-11-03 20:38 UTC from Coinbase Exchange public candles (1h, 1d). Data 2017-01-01 to 2026-11-02._

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
| BTC-USD | 1h | 86179 | 0.06% | 22.0% | none |
| BTC-USD | 1d | 3593 | 0.0% | 38.8% | 2017-04-15 |
| ETH-USD | 1h | 86194 | 0.04% | 19.6% | 2017-06-21 |
| ETH-USD | 1d | 3593 | 0.0% | 43.3% | 2017-06-21 |

A flash-crash wick on one exchange can trigger a resting stop far below the real market (ETH on Coinbase's exchange, 21 June 2017, traded near $0.10 for a moment). The engine fills such stops at the stop price, as a real stop order on that venue could have, so these bars can cause large one-day losses. 'Worst day' in the screen shows it.

## Benchmarks (buy and hold, no costs after entry)

| Asset | CAGR | Max DD | Sharpe |
|---|---|---|---|
| BTC-USD | 55.3% | -83.8% | 0.99 |
| ETH-USD | 76.6% | -94.0% | 1.08 |
| Cash | 0% | 0% | 0 |

## Headline: Robinhood fees, 5%-risk sizing (the rule maximum)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 109 | 26.6% | 1.099% | 1.63 | 9.6% | -31.4% | 0.55 | 53.1% | 185.7% | 20.8% | 3.6% | 6.2% | 0.19 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 109 | 26.6% | 1.099% | 1.63 | 9.6% | -31.4% | 0.55 | 53.1% | 185.7% | 20.8% | 3.6% | 6.2% | 0.19 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 9.261% | 4.06 | 30.8% | -38.7% | 0.99 | 41.7% | 610.4% | 27.9% | 57.1% | 15.4% | 0.31 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 84 | 50.0% | -0.559% | 0.41 | -4.9% | -38.7% | -0.7 | 7.5% | 49.8% | -3.6% | -3.3% | -7.1% | -0.76 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.958% | 0.63 | -46.5% | -99.9% | -1.27 | 52.4% | 291.8% | -20.4% | -52.1% | -57.1% | -2.26 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.85% | 0.11 | -88.3% | -100.0% | -7.51 | 7.3% | 98.3% | -87.8% | -87.4% | -89.4% | -8.03 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -2.012% | 0.17 | -42.2% | -99.6% | -2.79 | 3.2% | 96.8% | -39.4% | -47.9% | -39.7% | -3.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -1.606% | 0.46 | -5.2% | -52.8% | -0.5 | 2.8% | 19.6% | -8.3% | -9.7% | 0.9% | -0.45 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 0.796% | 1.71 | 2.5% | -14.3% | 0.33 | 4.3% | 38.5% | 7.0% | -0.8% | 1.8% | 0.07 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.516% | 0.82 | -6.8% | -73.7% | -0.25 | 14.5% | 166.8% | 16.2% | -9.9% | -19.5% | -1.26 |
| ETH-USD | trend_sma(n=100) | swing | 119 | 25.2% | 0.843% | 1.5 | 8.1% | -41.5% | 0.47 | 52.9% | 144.7% | 17.1% | 9.2% | 0.9% | -0.11 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 119 | 25.2% | 0.841% | 1.5 | 8.1% | -41.5% | 0.47 | 52.9% | 144.4% | 17.0% | 9.2% | 0.9% | -0.11 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 5.187% | 2.66 | 18.1% | -96.0% | 0.87 | 38.7% | 256.5% | -1.7% | 75.1% | 0.3% | 0.0 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 81 | 53.1% | -0.504% | 0.46 | -4.2% | -36.5% | -0.62 | 7.4% | 36.6% | -3.9% | -2.1% | -6.1% | -0.88 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.445% | 0.83 | -32.4% | -99.5% | -0.55 | 50.6% | 684.1% | -0.8% | -20.1% | -56.3% | -1.71 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.77% | 0.18 | -85.7% | -100.0% | -6.31 | 7.2% | 219.9% | -79.1% | -90.4% | -85.5% | -6.65 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -2.139% | 0.24 | -47.7% | -99.8% | -2.3 | 3.2% | 116.4% | -41.9% | -57.6% | -43.3% | -2.73 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.56% | 0.74 | -4.3% | -52.5% | -0.32 | 7.0% | 39.0% | -1.4% | -10.6% | -1.4% | -0.63 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 48.1% | 0.791% | 1.48 | 5.2% | -32.8% | 0.43 | 9.7% | 78.9% | 12.7% | -4.1% | 7.2% | 0.5 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.469% | 1.18 | 1.6% | -34.1% | 0.18 | 12.8% | 139.3% | 8.5% | -2.9% | -0.1% | -0.03 |

## Robinhood fees, 2%-risk sizing (same rules, smaller bets)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 109 | 26.6% | 0.455% | 1.66 | 4.6% | -14.5% | 0.55 | 53.1% | 48.6% | 8.9% | 2.0% | 3.5% | 0.22 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 109 | 26.6% | 0.455% | 1.66 | 4.6% | -14.5% | 0.55 | 53.1% | 48.6% | 8.9% | 2.0% | 3.5% | 0.22 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 4.035% | 4.15 | 17.0% | -21.7% | 0.99 | 41.7% | 99.5% | 15.0% | 31.3% | 8.4% | 0.39 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 84 | 50.0% | -0.224% | 0.41 | -1.9% | -17.4% | -0.71 | 7.5% | 22.8% | -1.4% | -1.3% | -2.8% | -0.77 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.426% | 0.67 | -23.6% | -94.7% | -1.04 | 52.4% | 255.1% | -4.3% | -24.9% | -34.9% | -1.88 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.78% | 0.1 | -87.3% | -100.0% | -7.65 | 7.3% | 99.8% | -85.5% | -86.1% | -89.4% | -8.05 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -1.835% | 0.12 | -39.1% | -99.2% | -2.92 | 3.2% | 88.7% | -34.9% | -43.0% | -39.2% | -3.07 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -0.663% | 0.46 | -2.1% | -26.0% | -0.51 | 2.8% | 9.1% | -3.3% | -3.9% | 0.4% | -0.46 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 0.318% | 1.7 | 1.1% | -5.9% | 0.32 | 4.3% | 13.9% | 2.9% | -0.3% | 0.7% | 0.06 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.095% | 0.92 | -1.4% | -41.2% | -0.1 | 14.5% | 77.2% | 10.6% | -2.7% | -9.0% | -1.24 |
| ETH-USD | trend_sma(n=100) | swing | 119 | 25.2% | 0.337% | 1.5 | 3.7% | -18.8% | 0.45 | 52.9% | 38.9% | 7.3% | 4.2% | 0.7% | -0.11 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 119 | 25.2% | 0.337% | 1.5 | 3.7% | -18.8% | 0.45 | 52.9% | 38.9% | 7.3% | 4.2% | 0.7% | -0.11 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 2.083% | 2.66 | 9.2% | -89.7% | 0.64 | 38.7% | 49.0% | 0.3% | 31.7% | 0.7% | -0.01 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 81 | 53.1% | -0.202% | 0.46 | -1.7% | -16.3% | -0.63 | 7.4% | 16.4% | -1.5% | -0.8% | -2.4% | -0.89 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.096% | 0.92 | -9.0% | -82.0% | -0.28 | 50.6% | 382.5% | 6.3% | -2.5% | -23.7% | -1.15 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.651% | 0.17 | -83.6% | -100.0% | -6.51 | 7.2% | 200.8% | -73.9% | -88.5% | -85.0% | -6.64 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -1.71% | 0.19 | -40.0% | -99.4% | -2.5 | 3.2% | 99.2% | -35.0% | -42.5% | -41.7% | -2.72 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.224% | 0.74 | -1.6% | -24.8% | -0.31 | 7.0% | 16.4% | -0.2% | -4.3% | -0.5% | -0.64 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 48.1% | 0.317% | 1.48 | 2.4% | -14.1% | 0.44 | 9.7% | 26.2% | 5.6% | -1.4% | 2.9% | 0.5 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.252% | 1.23 | 1.7% | -15.3% | 0.23 | 12.8% | 52.3% | 3.8% | 0.2% | 1.3% | 0.06 |

## Same rules at a 0.40% fee (assumed cheaper exchange), 5%-risk sizing

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 109 | 29.4% | 1.555% | 2.09 | 15.2% | -28.4% | 0.8 | 53.1% | 104.0% | 24.9% | 7.9% | 13.8% | 0.5 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 109 | 29.4% | 1.555% | 2.09 | 15.2% | -28.4% | 0.8 | 53.1% | 104.0% | 24.9% | 7.9% | 13.8% | 0.5 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 43.4% | 10.116% | 4.86 | 36.2% | -35.8% | 1.12 | 41.7% | 337.5% | 32.3% | 62.8% | 21.2% | 0.52 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 84 | 64.3% | -0.13% | 0.82 | -1.3% | -17.8% | -0.17 | 7.5% | 25.0% | -2.0% | -1.1% | -0.8% | -0.06 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 27.7% | -0.012% | 0.99 | -9.0% | -90.0% | -0.05 | 52.4% | 547.8% | 26.0% | -21.2% | -20.9% | -0.86 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 22.3% | -0.765% | 0.35 | -59.1% | -100.0% | -4.08 | 7.3% | 106.2% | -54.9% | -60.1% | -61.4% | -5.08 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 33.7% | -0.945% | 0.43 | -23.0% | -92.5% | -1.73 | 3.2% | 78.1% | -20.8% | -29.9% | -19.0% | -2.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -1.142% | 0.58 | -3.9% | -47.8% | -0.36 | 2.8% | 8.8% | -6.0% | -7.8% | 1.0% | -0.33 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 67.6% | 1.354% | 2.5 | 4.5% | -9.9% | 0.55 | 4.3% | 17.9% | 10.2% | 0.8% | 3.2% | 0.28 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 39.4% | 0.393% | 1.17 | 1.6% | -55.4% | 0.18 | 14.5% | 104.2% | 25.2% | -1.6% | -11.4% | -0.75 |
| ETH-USD | trend_sma(n=100) | swing | 119 | 26.1% | 1.194% | 1.83 | 12.7% | -30.4% | 0.67 | 52.9% | 76.4% | 20.1% | 13.3% | 6.9% | 0.17 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 119 | 26.1% | 1.192% | 1.83 | 12.7% | -30.4% | 0.67 | 52.9% | 76.2% | 20.1% | 13.3% | 6.9% | 0.17 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 41.5% | 5.907% | 3.15 | 22.5% | -95.9% | 0.94 | 38.7% | 136.2% | 1.6% | 79.8% | 5.0% | 0.17 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 81 | 61.7% | -0.188% | 0.76 | -1.7% | -24.6% | -0.24 | 7.4% | 17.5% | -2.4% | 0.0% | -2.5% | -0.45 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 29.3% | 0.379% | 1.18 | 4.9% | -87.2% | 0.33 | 50.6% | 1374.8% | 44.6% | 19.3% | -26.4% | -0.67 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 27.5% | -0.688% | 0.48 | -53.7% | -100.0% | -2.96 | 7.2% | 265.5% | -37.6% | -63.5% | -55.9% | -3.71 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 33.4% | -1.089% | 0.48 | -28.6% | -97.1% | -1.43 | 3.2% | 89.8% | -20.0% | -40.8% | -24.5% | -1.94 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 53.1% | -0.181% | 0.91 | -1.9% | -40.5% | -0.11 | 7.0% | 18.4% | 2.8% | -8.0% | -0.5% | -0.48 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 55.7% | 1.208% | 1.82 | 8.7% | -24.2% | 0.67 | 9.7% | 39.2% | 17.2% | 0.6% | 9.0% | 0.7 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 42.4% | 1.213% | 1.54 | 8.2% | -30.3% | 0.48 | 12.8% | 82.1% | 14.7% | 4.2% | 6.6% | 0.3 |

## Before fees (slippage only), 5%-risk sizing

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 109 | 32.1% | 1.89% | 2.55 | 19.4% | -26.2% | 0.98 | 53.1% | 0.0% | 27.9% | 11.2% | 19.7% | 0.73 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 109 | 32.1% | 1.89% | 2.55 | 19.4% | -26.2% | 0.98 | 53.1% | 0.0% | 27.9% | 11.2% | 19.7% | 0.73 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 43.4% | 10.743% | 5.61 | 40.3% | -33.6% | 1.22 | 41.7% | 0.0% | 35.6% | 67.2% | 25.7% | 0.68 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 84 | 72.6% | 0.186% | 1.29 | 1.4% | -14.3% | 0.25 | 7.5% | 0.0% | -0.9% | 0.5% | 4.0% | 0.49 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 34.2% | 0.683% | 1.49 | 34.0% | -50.3% | 0.99 | 52.4% | 0.0% | 76.2% | 13.2% | 23.5% | 0.41 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 36.8% | 0.032% | 1.05 | 1.8% | -41.6% | 0.19 | 7.3% | 0.0% | 16.6% | -7.5% | -1.2% | -0.2 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 39.1% | -0.161% | 0.86 | -5.1% | -57.4% | -0.36 | 3.2% | 0.0% | -3.7% | -13.0% | 0.4% | -0.42 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 30 | 43.3% | -0.802% | 0.68 | -2.9% | -43.9% | -0.26 | 2.8% | 0.0% | -4.2% | -6.5% | 1.1% | -0.23 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 73.5% | 1.764% | 3.22 | 6.0% | -8.9% | 0.72 | 4.3% | 0.0% | 12.6% | 1.9% | 4.2% | 0.44 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 43.6% | 1.06% | 1.53 | 8.3% | -39.4% | 0.51 | 14.5% | 0.0% | 32.1% | 4.9% | -5.0% | -0.33 |
| ETH-USD | trend_sma(n=100) | swing | 119 | 26.9% | 1.451% | 2.15 | 16.2% | -26.9% | 0.82 | 52.9% | 0.0% | 22.4% | 16.4% | 11.5% | 0.38 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 119 | 26.9% | 1.449% | 2.15 | 16.2% | -26.9% | 0.82 | 52.9% | 0.0% | 22.4% | 16.4% | 11.5% | 0.38 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 45.3% | 6.435% | 3.59 | 25.7% | -95.8% | 0.99 | 38.7% | 0.0% | 4.0% | 83.3% | 8.7% | 0.29 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 81 | 65.4% | 0.044% | 1.06 | 0.2% | -17.8% | 0.06 | 7.4% | 0.0% | -1.3% | 1.7% | 0.3% | -0.11 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 34.0% | 0.983% | 1.59 | 44.6% | -54.7% | 1.04 | 50.6% | 0.0% | 90.4% | 59.7% | 7.6% | 0.19 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 39.5% | 0.107% | 1.14 | 8.9% | -66.8% | 0.47 | 7.2% | 0.0% | 38.5% | -3.5% | -0.7% | -0.13 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 38.0% | -0.319% | 0.8 | -10.5% | -79.1% | -0.47 | 3.2% | 0.0% | 1.0% | -24.4% | -7.0% | -0.77 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 53.1% | 0.097% | 1.05 | -0.1% | -29.9% | 0.05 | 7.0% | 0.0% | 5.9% | -6.1% | 0.2% | -0.36 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 79 | 58.2% | 1.513% | 2.12 | 11.4% | -18.9% | 0.85 | 9.7% | 0.0% | 20.5% | 4.2% | 10.4% | 0.84 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 49.4% | 1.759% | 1.9 | 13.4% | -27.3% | 0.71 | 12.8% | 0.0% | 19.4% | 9.7% | 11.8% | 0.56 |

## Robinhood fees, full sizing (ignores the 5% rule; for comparison)

| Asset | Strategy | Style | Trades | Win% | Exp/trade | PF | CAGR | Max DD | Sharpe | Exposure | Fees paid | 2017-19 | 2020-22 | 2023-now | Test Sharpe (2022+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | swing | 109 | 26.6% | 3.017% | 1.62 | 14.8% | -75.1% | 0.53 | 53.1% | 856.8% | 45.1% | 6.4% | 1.5% | -0.01 |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | swing | 109 | 26.6% | 2.074% | 1.65 | 14.7% | -48.6% | 0.57 | 53.1% | 580.4% | 42.8% | 5.3% | 3.4% | 0.06 |
| BTC-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 11.643% | 3.45 | 37.4% | -57.6% | 0.94 | 41.7% | 1447.2% | 51.6% | 57.1% | 14.8% | 0.16 |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 84 | 50.0% | -1.124% | 0.56 | -10.9% | -70.7% | -0.39 | 7.5% | 96.1% | -11.4% | -10.9% | -10.6% | -0.52 |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | swing | 549 | 22.6% | -0.982% | 0.68 | -50.2% | -100.0% | -1.03 | 52.4% | 398.2% | -21.6% | -60.3% | -58.1% | -2.24 |
| BTC-USD | intraday_breakout(look=24,hold=12) | day | 1122 | 12.1% | -1.853% | 0.11 | -88.4% | -100.0% | -7.5 | 7.3% | 98.3% | -87.9% | -87.5% | -89.4% | -8.03 |
| BTC-USD | intraday_meanrev(buy_below=25) | day | 261 | 19.2% | -1.963% | 0.21 | -41.7% | -99.5% | -2.67 | 3.2% | 107.0% | -38.1% | -47.6% | -39.7% | -3.06 |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 32 | 43.8% | -3.847% | 0.48 | -14.6% | -86.3% | -0.5 | 3.0% | 32.9% | -26.3% | -21.1% | 1.9% | -0.46 |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 34 | 58.8% | 2.377% | 1.99 | 7.1% | -30.0% | 0.42 | 4.3% | 113.6% | 25.5% | -3.8% | 3.0% | -0.05 |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 94 | 34.0% | -0.674% | 0.82 | -9.5% | -79.2% | -0.25 | 14.5% | 184.6% | 12.2% | -12.8% | -21.1% | -1.32 |
| ETH-USD | trend_sma(n=100) | swing | 119 | 25.2% | 3.192% | 1.48 | 5.8% | -91.4% | 0.43 | 52.9% | 660.0% | 35.1% | -3.9% | -5.8% | -0.23 |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | swing | 119 | 25.2% | 1.208% | 1.37 | 7.6% | -68.9% | 0.38 | 52.9% | 298.4% | 19.4% | 10.3% | -2.8% | -0.18 |
| ETH-USD | donchian(entry_n=20,exit_n=10) | swing | 53 | 39.6% | 9.68% | 2.88 | 27.8% | -97.1% | 0.97 | 38.7% | 1054.1% | 0.8% | 140.8% | -6.2% | -0.09 |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | swing | 81 | 53.1% | -1.457% | 0.58 | -14.4% | -82.0% | -0.35 | 7.4% | 81.3% | -17.2% | -12.5% | -13.7% | -0.78 |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | swing | 526 | 24.5% | -0.513% | 0.87 | -46.7% | -100.0% | -0.44 | 50.6% | 581.6% | -30.2% | -36.0% | -62.8% | -1.78 |
| ETH-USD | intraday_breakout(look=24,hold=12) | day | 1056 | 17.1% | -1.782% | 0.18 | -85.9% | -100.0% | -6.25 | 7.2% | 216.8% | -80.0% | -90.5% | -85.5% | -6.65 |
| ETH-USD | intraday_meanrev(buy_below=25) | day | 287 | 24.7% | -2.1% | 0.3 | -47.7% | -99.9% | -2.03 | 3.2% | 149.7% | -38.7% | -59.9% | -43.3% | -2.73 |
| ETH-USD | drop_bounce(drop_pct=10.0,hold=5) | pattern | 64 | 51.6% | -0.418% | 0.93 | -9.2% | -84.1% | -0.07 | 7.0% | 115.3% | -2.7% | -23.4% | -1.8% | -0.51 |
| ETH-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | pattern | 80 | 47.5% | 1.885% | 1.38 | 4.5% | -77.9% | 0.31 | 9.9% | 283.1% | 22.4% | -16.8% | 10.4% | 0.19 |
| ETH-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | pattern | 85 | 37.6% | 0.595% | 1.15 | -0.1% | -54.6% | 0.16 | 12.8% | 231.8% | 19.0% | -12.3% | -3.5% | -0.13 |

## Screen for paper trading (Robinhood costs; 5% and 2% risk sizing)

Pass = 30+ trades, positive expectancy after costs, profit factor 1.2+, max drawdown no worse than -20%, Sharpe above the same asset's buy-and-hold, positive in 2 of 3 periods, positive Sharpe in 2022+.

| Asset | Strategy | Sizing | Result | Why | Worst day | Approx. breakeven fee per side |
|---|---|---|---|---|---|---|
| BTC-USD | trend_sma(n=100) | risk5 | fail | max drawdown -31.4% worse than -20%; Sharpe 0.55 not above buy-and-hold 0.99 | -9.3% | 2.357% |
| BTC-USD | trend_sma(n=100) | risk2 | fail | Sharpe 0.55 not above buy-and-hold 0.99 | -4.5% | 2.401% |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | risk5 | fail | max drawdown -31.4% worse than -20%; Sharpe 0.55 not above buy-and-hold 0.99 | -9.3% | 2.357% |
| BTC-USD | trend_voltarget(n=100,vol=0.4) | risk2 | fail | Sharpe 0.55 not above buy-and-hold 0.99 | -4.5% | 2.401% |
| BTC-USD | donchian(entry_n=20,exit_n=10) | risk5 | fail | max drawdown -38.7% worse than -20%; Sharpe 0.99 not above buy-and-hold 0.99 | -12.7% | 7.899% |
| BTC-USD | donchian(entry_n=20,exit_n=10) | risk2 | fail | max drawdown -21.7% worse than -20%; Sharpe 0.99 not above buy-and-hold 0.99 | -8.4% | 7.859% |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.41 < 1.2; max drawdown -38.7% worse than -20%; Sharpe -0.7 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.7% | 0.236% |
| BTC-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.41 < 1.2; Sharpe -0.71 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -2.7% | 0.234% |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.63 < 1.2; max drawdown -99.9% worse than -20%; Sharpe -1.27 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.8% | 0.395% |
| BTC-USD | ema_cross_4h(fast=20,slow=50) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.67 < 1.2; max drawdown -94.7% worse than -20%; Sharpe -1.04 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.6% | 0.487% |
| BTC-USD | intraday_breakout(look=24,hold=12) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.11 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -7.51 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -16.6% | 0.016% |
| BTC-USD | intraday_breakout(look=24,hold=12) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.1 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -7.65 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.2% | 0.029% |
| BTC-USD | intraday_meanrev(buy_below=25) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.17 < 1.2; max drawdown -99.6% worse than -20%; Sharpe -2.79 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -12.5% | 0.0% |
| BTC-USD | intraday_meanrev(buy_below=25) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.12 < 1.2; max drawdown -99.2% worse than -20%; Sharpe -2.92 not above buy-and-hold 0.99; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.8% | 0.0% |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; max drawdown -52.8% worse than -20%; Sharpe -0.5 not above buy-and-hold 0.99; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.2% | 0.0% |
| BTC-USD | drop_bounce(drop_pct=10.0,hold=5) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; max drawdown -26.0% worse than -20%; Sharpe -0.51 not above buy-and-hold 0.99; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -2.9% | 0.0% |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk5 | fail | Sharpe 0.33 not above buy-and-hold 0.99 | -5.8% | 1.778% |
| BTC-USD | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | risk2 | fail | Sharpe 0.32 not above buy-and-hold 0.99 | -2.3% | 1.774% |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.82 < 1.2; max drawdown -73.7% worse than -20%; Sharpe -0.25 not above buy-and-hold 0.99; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.641% |
| BTC-USD | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.92 < 1.2; max drawdown -41.2% worse than -20%; Sharpe -0.1 not above buy-and-hold 0.99; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -3.7% | 0.826% |
| ETH-USD | trend_sma(n=100) | risk5 | fail | max drawdown -41.5% worse than -20%; Sharpe 0.47 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -13.2% | 2.348% |
| ETH-USD | trend_sma(n=100) | risk2 | fail | Sharpe 0.45 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -6.6% | 2.362% |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | risk5 | fail | max drawdown -41.5% worse than -20%; Sharpe 0.47 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -13.2% | 2.345% |
| ETH-USD | trend_voltarget(n=100,vol=0.4) | risk2 | fail | Sharpe 0.45 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -6.6% | 2.362% |
| ETH-USD | donchian(entry_n=20,exit_n=10) | risk5 | fail | max drawdown -96.0% worse than -20%; Sharpe 0.87 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -95.0% | 5.371% |
| ETH-USD | donchian(entry_n=20,exit_n=10) | risk2 | fail | max drawdown -89.7% worse than -20%; Sharpe 0.64 not above buy-and-hold 1.08; not positive out-of-sample (2022+) | -88.1% | 5.383% |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; max drawdown -36.5% worse than -20%; Sharpe -0.62 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.076% |
| ETH-USD | rsi2_meanrev(buy_below=10,trend_n=200) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.46 < 1.2; Sharpe -0.63 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -2.7% | 0.078% |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.83 < 1.2; max drawdown -99.5% worse than -20%; Sharpe -0.55 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -16.1% | 0.656% |
| ETH-USD | ema_cross_4h(fast=20,slow=50) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.92 < 1.2; max drawdown -82.0% worse than -20%; Sharpe -0.28 not above buy-and-hold 1.08; positive in only 1 of 3 periods; not positive out-of-sample (2022+) | -6.8% | 0.816% |
| ETH-USD | intraday_breakout(look=24,hold=12) | risk5 | fail | expectancy <= 0 after costs; profit factor 0.18 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -6.31 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -11.9% | 0.054% |
| ETH-USD | intraday_breakout(look=24,hold=12) | risk2 | fail | expectancy <= 0 after costs; profit factor 0.17 < 1.2; max drawdown -100.0% worse than -20%; Sharpe -6.51 not above buy-and-hold 1.08; positive in only 0 of 3 periods; not positive out-of-sample (2022+) | -9.8% | 0.053% |
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
| BTC-USD | ema_cross_4h | ema_cross_4h(fast=50,slow=200) | -0.21 | -1.67 | -50.7% | -2.26 | 3 |
| BTC-USD | intraday_breakout | intraday_breakout(look=48,hold=24) | -5.43 | -5.49 | -68.6% | -8.03 | 3 |
| BTC-USD | intraday_meanrev | intraday_meanrev(buy_below=20) | -1.75 | -1.75 | -16.0% | -3.06 | 3 |
| BTC-USD | momentum_burst | momentum_burst(lookback=3,thresh_pct=15.0,hold=5) | 0.49 | 0.07 | 0.2% | 0.07 | 3 |
| BTC-USD | rsi2_meanrev | rsi2_meanrev(buy_below=5,trend_n=200) | -0.49 | -0.38 | -2.1% | -0.76 | 3 |
| BTC-USD | squeeze_breakout | squeeze_breakout(squeeze_n=30,breakout_n=20,hold=15) | 1.0 | -0.09 | -2.4% | -1.26 | 2 |
| BTC-USD | trend_sma | trend_sma(n=50) | 1.0 | 0.44 | 7.1% | 0.19 | 4 |
| BTC-USD | trend_voltarget | trend_voltarget(n=100,vol=0.3) | 0.88 | 0.19 | 1.8% | 0.19 | 3 |
| ETH-USD | donchian | donchian(entry_n=20,exit_n=10) | 1.29 | 0.0 | -3.1% | 0.0 | 3 |
| ETH-USD | drop_bounce | drop_bounce(drop_pct=15.0,hold=7) | -0.12 | -0.17 | -0.6% | -0.63 | 3 |
| ETH-USD | ema_cross_4h | ema_cross_4h(fast=50,slow=200) | 0.55 | -1.3 | -47.4% | -1.71 | 3 |
| ETH-USD | intraday_breakout | intraday_breakout(look=48,hold=24) | -4.89 | -4.84 | -68.9% | -6.65 | 3 |
| ETH-USD | intraday_meanrev | intraday_meanrev(buy_below=20) | -1.61 | -1.49 | -17.4% | -2.73 | 3 |
| ETH-USD | momentum_burst | momentum_burst(lookback=5,thresh_pct=20.0,hold=7) | 0.69 | 0.54 | 3.6% | 0.5 | 3 |
| ETH-USD | rsi2_meanrev | rsi2_meanrev(buy_below=5,trend_n=200) | -0.32 | -0.25 | -1.5% | -0.88 | 3 |
| ETH-USD | squeeze_breakout | squeeze_breakout(squeeze_n=20,breakout_n=10,hold=10) | 0.34 | -0.03 | -2.3% | -0.03 | 2 |
| ETH-USD | trend_sma | trend_sma(n=50) | 1.08 | 0.28 | 3.6% | -0.11 | 4 |
| ETH-USD | trend_voltarget | trend_voltarget(n=100,vol=0.4) | 0.93 | -0.11 | -3.7% | -0.11 | 3 |

## Caveats

- One exchange's history (Coinbase). Real fills on Robinhood can differ; paper trading measures that.
- Daily and 4h strategies can gap through stops overnight-style in crypto's 24/7 market; 'worst trade' shows the real damage.
- Sharpe uses daily returns x sqrt(365). Cash earns 0% here; stablecoin yield would help flat periods slightly.
- A backtest pass is a reason to paper trade, not to trade live.
