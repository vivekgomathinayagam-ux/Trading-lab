# Scalp backtest results (2026-11-18 03:12 UTC)

Variants tried (setup x window x side x target x stop): **480**. Profitable in train: 0; in validation: 0; in both with >=300 trades each: **0**. Expected false positives are large when 480 configs are tried; read the holdout, not the train numbers.

Random-entry control = same exits applied to every eligible bar (mean net bps by split) is in grid_pooled.csv.

## Top configs by min(train, validation) net bps, then HOLDOUT

| setup | win | side | T% | S% | train bps (n) | val bps (n) | **holdout bps (n)** | hold PF | hold 95% CI bps | control hold bps | hold $/trade | hold $/day | tickers + / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *no config was profitable in both train and validation with enough trades* | | | | | | | | | | | | | |

## By setup: share of the configs that were profitable (net) per split

| setup | train | val | hold |
|---|---|---|---|
| orb15 | 0% | 0% | 0% |
| vwap_reclaim | 0% | 0% | 0% |
| ema_fast_cross | 0% | 0% | 0% |
| rsi3_fade | 0% | 0% | 0% |
| vol_spike_mom | 0% | 0% | 0% |

Random-entry control, mean net bps per trade: train: -5.48, val: -5.42, hold: -5.48

## Per ticker group, same top configs, holdout net bps (pooled)

| setup | win | side | T | S | orig | etf_added | low_priced | stress |
|---|---|---|---|---|---|---|---|---|
