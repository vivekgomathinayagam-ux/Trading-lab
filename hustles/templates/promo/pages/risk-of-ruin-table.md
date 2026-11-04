# Risk of Ruin Table: How Often Does a Fixed Risk % Halve an Account? (free, simulated)

Arithmetic and simulation only. Not advice, not a signal, no prediction of your results. Options involve risk of loss. Every number below is from a script (20,000 random paths per row, fixed seed), using made-up win rates and payoffs. Written with AI assistance (Claude).

## Setup

Each trade risks a fixed % of current equity. A win pays `win size x risk`; a loss costs exactly the risk. "Halved" means equity touches 50% of the start within 200 trades. Costs and slippage are ignored here, so real odds are somewhat worse.

## Results

| Win rate | Win size (R) | Expectancy/trade | Risk per trade | Chance account halves within 200 trades |
|---|---|---|---|---|
| 40% | 1.5R | +0.00R | 1% | 0.0% |
| 40% | 1.5R | +0.00R | 2% | 5.8% |
| 40% | 1.5R | +0.00R | 5% | 55.3% |
| 40% | 1.5R | +0.00R | 10% | 87.6% |
| 50% | 1.0R | +0.00R | 1% | 0.0% |
| 50% | 1.0R | +0.00R | 2% | 2.0% |
| 50% | 1.0R | +0.00R | 5% | 43.1% |
| 50% | 1.0R | +0.00R | 10% | 80.5% |
| 50% | 1.5R | +0.25R | 1% | 0.0% |
| 50% | 1.5R | +0.25R | 2% | 0.0% |
| 50% | 1.5R | +0.25R | 5% | 1.6% |
| 50% | 1.5R | +0.25R | 10% | 17.7% |
| 60% | 1.0R | +0.20R | 1% | 0.0% |
| 60% | 1.0R | +0.20R | 2% | 0.0% |
| 60% | 1.0R | +0.20R | 5% | 0.6% |
| 60% | 1.0R | +0.20R | 10% | 10.6% |

## What the table shows

- With **zero edge** (first row of each block, expectancy 0.00R), risking 1% almost never halves the account in 200 trades, but risking 5% does more often than not (43-55%), and 10% usually does (80%+).
- Even with a **positive edge** (+0.20R to +0.25R per trade), 10% risk per trade still halves the account 10-18% of the time. Position size, not only the strategy, decides survival.
- This is why a per-trade cap such as 1-2% and a daily loss limit exist. See the position-size cheat sheet and the daily-loss-limit page.
- A simulation with an assumed win rate is not your win rate. Log real trades and compute your own expectancy (see the R-multiple page).

## Want it ready-made?

The **Trader Toolkit** ($12, built with AI assistance) has a risk and position-size calculator with a risk-limit check, a journal with R stats, and a trading-plan checklist pack: https://vivekgo8.gumroad.com/l/aobhdm
