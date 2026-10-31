# Combos (pre-registered)

Write each combo here BEFORE looking at any result: date registered, class (A/B/C), rule, why it should work, what would prove it wrong. A combo is judged only on days after its registration date.

(none yet)

## C-1 (registered 2026-10-28, class B, judged on days after Oct 28 only)
- **Rule:** `cvd_tqqq` and `volspike` both long TQQQ the same day -> count as one "confluence" trade (record only; no new desk).
- **Why:** both read buying pressure from volume; agreement should filter noise.
- **Wrong if:** after 10+ confluence days, the confluence trades' mean is no better than either desk alone on the same days.

## C-2 (registered 2026-10-31, class B, judged only on sessions from Nov 2, 2026)
- **Rule:** split `volspike` trades by the SPY 0DTE board at 10:00 ET (Heatseeker, `max_expirations=1`, 30 strikes, net gamma = sum): net < 0 vs net >= 0. Record only; no desk changes.
- **Why:** with negative dealer gamma, hedging adds to moves, so a breakout on a volume spike should follow through more. Honest caveat: suggested by 5 already-seen days (3 negative days avg +1.31%, 2 positive −0.14%), and pilots 1-2 found no range difference by gamma sign. Those 5 days never count.
- **Wrong if:** after 10+ volspike trades from Nov 2, the mean on negative-gamma days is not higher than on positive-gamma days, or the difference's bootstrap CI includes 0 at 20+ trades.
