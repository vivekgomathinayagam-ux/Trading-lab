"""Parity replay: run paper days through the lab (shared core) on archived 1-minute bars and
compare the trades with the paper ledger (ledger/daytrade_trades.csv on branch `data`).

  python -m lab.floor.replay --archive backtests/data/etf1m --trades ledger/daytrade_trades.csv \
      --start 2026-10-26 [--end 2026-10-27] [--out parity.md]

A trade "matches" when the same desk trades the same symbol on the same day, the entry minute is
within 2 minutes (the bot enters on the live price at the signal bar's close, the lab at the next
bar's open), and the exit reason agrees (paper 'eod' / 'eod_safety' == lab 'eod'). Price gaps are
reported in % so a data problem shows up even when the trade list matches.

The lab books start at $1,000 on --start, exactly like the paper books. All bars before --start
are warm-up only (features, no trading).
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from pathlib import Path

from strategies.daytrade.core import PAPER_RULES, SYMBOLS, Bar

from .data import NY, load_archive
from .engine import simulate

ENTRY_TOL_MIN = 2
# first paper day per desk (desks added later are not compared before they existed)
DESK_PAPER_START = {"orb_vol": "2026-10-26", "ema_vol": "2026-10-26", "volspike": "2026-10-26",
                    "ema_vol_v2": "2026-10-29", "cvd_spy": "2026-10-29", "cvd_tqqq": "2026-10-29"}


def load_paper(path: Path) -> list[dict]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def lab_trades(bars: dict[str, list[Bar]], start: date, end: date, rules=None) -> list[dict]:
    clip = {s: [b for b in v if b.t.date() <= end] for s, v in bars.items()}
    res = simulate(clip, rules or PAPER_RULES, trade_from_day=start)
    out = []
    for d in res["desks"]:
        first = max(start.isoformat(), DESK_PAPER_START.get(d.key, start.isoformat()))
        out += [t for t in d.trades if first <= t["entry_t"][:10] <= end.isoformat()]
    return out


def _minute(ts: str) -> datetime:
    return datetime.fromisoformat(ts).astimezone(NY).replace(second=0, microsecond=0)


def _norm_reason(r: str) -> str:
    return "eod" if r in ("eod", "eod_safety", "end") else r


def compare(paper: list[dict], lab: list[dict], start: date, end: date) -> dict:
    def in_window(t):
        return start.isoformat() <= t["entry_t"][:10] <= end.isoformat()
    P = [t for t in paper if in_window(t)]
    key = lambda t: (t["desk"], t["entry_t"][:10])  # noqa: E731  one entry per desk per day
    pk = {key(t): t for t in P}
    lk = {key(t): t for t in lab}
    rows, mism = [], 0
    for k in sorted(set(pk) | set(lk)):
        p, l = pk.get(k), lk.get(k)
        row = {"desk": k[0], "day": k[1], "paper": None, "lab": None, "status": ""}
        if p:
            row["paper"] = f"{p['sym']} {p['entry_t'][11:16]} @{float(p['entry_px']):.2f} -> {p['reason']} @{float(p['exit_px']):.2f}"
        if l:
            row["lab"] = f"{l['sym']} {l['entry_t'][11:16]} @{l['entry_px']:.2f} -> {l['reason']} @{l['exit_px']:.2f}"
        if p and l:
            dt = abs((_minute(p["entry_t"]) - _minute(l["entry_t"])).total_seconds()) / 60
            same = (p["sym"] == l["sym"] and dt <= ENTRY_TOL_MIN and _norm_reason(p["reason"]) == _norm_reason(l["reason"]))
            row["entry_gap_pct"] = round((float(p["entry_px"]) / l["entry_px"] - 1) * 100, 3)
            row["exit_gap_pct"] = round((float(p["exit_px"]) / l["exit_px"] - 1) * 100, 3)
            row["entry_minutes_apart"] = dt
            row["status"] = "match" if same else "DIFF"
        else:
            row["status"] = "paper only" if p else "lab only"
        if row["status"] != "match":
            mism += 1
        rows.append(row)
    return {"rows": rows, "mismatches": mism, "paper_trades": len(P), "lab_trades": len(lab),
            "start": start.isoformat(), "end": end.isoformat()}


def to_markdown(r: dict) -> str:
    L = [f"# Parity replay {r['start']} to {r['end']}", "",
         f"Paper trades {r['paper_trades']}, lab trades {r['lab_trades']}, mismatches **{r['mismatches']}**.", "",
         "| Desk | Day | Paper | Lab | Entry gap | Exit gap | Status |", "|---|---|---|---|---|---|---|"]
    for x in r["rows"]:
        L.append(f"| {x['desk']} | {x['day']} | {x['paper'] or '-'} | {x['lab'] or '-'} | "
                 f"{x.get('entry_gap_pct', '')} | {x.get('exit_gap_pct', '')} | {x['status']} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--trades", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    bars = {}
    for s in SYMBOLS:
        p = Path(a.archive) / f"{s}.csv.gz"
        if p.exists():
            d = load_archive(p)
            bars[s] = [d[k] for k in sorted(d)]
    start = date.fromisoformat(a.start)
    last = max(b.t.date() for v in bars.values() for b in v)
    end = date.fromisoformat(a.end) if a.end else last
    end = min(end, last)
    r = compare(load_paper(Path(a.trades)), lab_trades(bars, start, end), start, end)
    md = to_markdown(r)
    if a.out:
        Path(a.out).write_text(md)
    print(md)
    return 0 if r["mismatches"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
