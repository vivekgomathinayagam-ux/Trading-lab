"""Read-only paper-desk logging (2026-11-17). Writes two CSVs next to the other ledger files:

- daytrade_bars_<day>.csv: every 1-minute bar the bot acts on, with the time it saw it, so parity
  replays compare bar by bar (Yahoo revises bars after the fact; QUEUE 2).
- daytrade_entry_context.csv: market context at each paper entry (extension from the open,
  distance from the session high/low, ATR %, VWAP distance) for the entry-quality shadow tests
  (QUEUE 4a).

Logging only. Every write is wrapped: a failure here must never touch a desk, order or price.
"""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger("barlog")
BAR_COLS = ["sym", "bar_start", "o", "h", "l", "c", "v", "seen_at", "fresh", "latest_in_step"]
CTX_COLS = ["desk", "sym", "bar_start", "entered_at", "fill_px", "ret_open_pct", "dist_high_pct",
            "dist_low_pct", "atr14_pct", "vwap_dist_pct", "bars_in_session"]


class BarLog:
    def __init__(self, ledger_dir: Path):
        self.dir = ledger_dir                   # bars go to one file per day (keeps pushes small)
        self.ctx_path = ledger_dir / "daytrade_entry_context.csv"
        self.sess: dict[str, list] = {}          # sym -> today's bars (o, h, l, c, v)
        self.day: dict[str, str] = {}

    def _append(self, path: Path, cols: list[str], row: dict) -> None:
        try:
            new = not path.exists()
            with path.open("a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols)
                if new:
                    w.writeheader()
                w.writerow(row)
        except Exception as e:  # noqa: BLE001
            log.error("barlog write failed (%s): %s", path.name, e)

    def bar(self, sym: str, b, seen_at: datetime, fresh: bool, latest: bool) -> None:
        try:
            d = b.t.date().isoformat()
            if self.day.get(sym) != d:
                self.day[sym], self.sess[sym] = d, []
            self.sess[sym].append((b.o, b.h, b.l, b.c, b.v))
            self._append(self.dir / f"daytrade_bars_{d}.csv", BAR_COLS, {
                "sym": sym, "bar_start": b.t.isoformat(), "o": b.o, "h": b.h, "l": b.l, "c": b.c,
                "v": b.v, "seen_at": seen_at.isoformat(timespec="seconds"), "fresh": bool(fresh),
                "latest_in_step": bool(latest)})
        except Exception as e:  # noqa: BLE001
            log.error("barlog bar failed: %s", e)

    def entry(self, desk: str, sym: str, bar_t, fill_px: float, now: datetime) -> None:
        try:
            s = self.sess.get(sym) or []
            if not s:
                return
            px = s[-1][3]
            op = s[0][0]
            hi, lo = max(x[1] for x in s), min(x[2] for x in s)
            tr = [max(x[1] - x[2], abs(x[1] - s[i - 1][3]), abs(x[2] - s[i - 1][3])) if i else x[1] - x[2]
                  for i, x in enumerate(s)]
            atr = sum(tr[-14:]) / len(tr[-14:])
            pv = sum(((x[1] + x[2] + x[3]) / 3) * x[4] for x in s)
            vv = sum(x[4] for x in s)
            vwap = pv / vv if vv else px
            r = lambda x: round(x, 4)  # noqa: E731
            self._append(self.ctx_path, CTX_COLS, {
                "desk": desk, "sym": sym, "bar_start": bar_t.isoformat() if bar_t else "",
                "entered_at": now.isoformat(timespec="seconds"), "fill_px": r(fill_px),
                "ret_open_pct": r((px / op - 1) * 100), "dist_high_pct": r((px / hi - 1) * 100),
                "dist_low_pct": r((px / lo - 1) * 100), "atr14_pct": r(atr / px * 100),
                "vwap_dist_pct": r((px / vwap - 1) * 100), "bars_in_session": len(s)})
        except Exception as e:  # noqa: BLE001
            log.error("barlog entry failed: %s", e)
