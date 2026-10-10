# ORB — Opening Range Breakout (SPY, TQQQ)
Stage: spec. Gomes's design: Pine Script signal layer + Python backtest layer.
Hypothesis: a break of the opening range (first N minutes) continues in the break direction often enough to pay after costs.
Instruments: SPY, TQQQ (treated separately; TQQQ is 3x leveraged).
Entry / exit / stop / sizing / holding time: to be pinned in Phase 0 step 7 from Gomes's existing Pine logic.
What proves it wrong: expectancy after costs <= 0 over the out-of-sample window, or profit factor < 1.2.
