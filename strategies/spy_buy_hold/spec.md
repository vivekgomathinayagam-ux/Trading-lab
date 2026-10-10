# Control: SPY buy-and-hold

**Hypothesis:** doing nothing beats most active setups after costs. Every other
setup must beat this on risk-adjusted return to earn a live slot.

- Instruments: SPY (whole shares; fractional once confirmed)
- Entry: at the first loop after the stage becomes `paper`, buy the largest
  whole-share quantity whose cost fits settled cash and whose worst case
  (a 100% loss is not the measure; we use a 5% stop-equivalent for the per-trade
  cap: max_loss = 5% of equity) passes the risk engine.
- Exit: none (hold). Retired only by decision.
- Sizing: all settled cash, sized against the live-size account.
- Proof-wrong: n/a; it is the benchmark.
