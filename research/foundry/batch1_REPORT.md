# Foundry batch 1: result (2026-11-03)

Pre-registration: `PREREG.md`, committed (3b05704) before any result was computed.
- Code: `lab/foundry/rules.py`. No-look-ahead test: `lab/tests/test_foundry.py`.
- Raw results: `data:backtests/foundry/latest/`.
- Costs: 0.046% round trip. "Exp" is net % per trade.

| Rule | 1-min, 26 sessions: trades / exp / PF / halves | 5-min, 41 sessions: trades / exp / PF / halves | Verdict |
|---|---|---|---|
| F1 cloud ride (slow-cloud exit) | 115 / −0.006 / 0.96 / −0.03, +0.02 | 177 / −0.023 / 0.84 / −0.05, +0.00 | refuted |
| F2 cloud ride (fast-cloud exit) | 154 / +0.013 / 1.14 / +0.00, +0.02 | 243 / −0.014 / 0.85 / −0.05, +0.02 | refuted |
| F3 VWAP trend | 94 / +0.008 / 1.09 / −0.02, +0.03 | 149 / −0.023 / 0.73 / −0.06, +0.02 | refuted |
| F4 trend break (12-bar VWAP run, then the break) | 39 / −0.015 / 0.89 / +0.05, −0.09 | 63 / −0.015 / 0.87 / −0.03, −0.00 | refuted |
| F5 Fib 50-61.8 pullback | 21 / +0.038 / 1.41 / +0.04, +0.04 | 49 / −0.050 / 0.64 / −0.05, −0.05 | refuted |
| F6 Fib 38.2-50 pullback | 37 / −0.061 / 0.47 / −0.08, −0.04 | 73 / −0.061 / 0.51 / −0.08, −0.04 (CI below 0) | refuted |
| C1 long 09:45 → 15:55 (control) | 52 / −0.133 | 82 / −0.078 | regime: down-drift |

## What we learned
- **No rule passed.** None of the six met the pre-registered bar on either sample.
- **Shorts beat longs, but that is the period, not an edge.** In 5 of 6 rules the short side beat the long side, because Sep-Nov 2026 drifted down. A rule has to work on both sides to count.
- **Costs decide trend-following on SPY/QQQ.** Gross edge per trade is about the size of the round-trip cost. Two ways forward: fewer, bigger trades (gate to trend days), or a cheaper vehicle.
- **The small first sample flattered F5.** Two samples are now standard.

## What it would have done on the days Vivek flagged
- **Nov 2:** F1 short QQQ +1.17%, F2 short QQQ +1.29%, F4 short SPY +0.95%. The rules catch big trend days.
- **The rest of the time** they give it back in chop. That is why a trend-day gate is the next test (see `research/BOARD.md`).
- **Nov 3** will be in tonight's post-mortem.
