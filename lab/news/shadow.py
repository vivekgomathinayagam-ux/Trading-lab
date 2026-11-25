"""Newsie shadow test (standing, PREREG_batch6 / batch8): replay each paper desk's trades on Newsie
days with (a) sit_out = no entries, (b) caution = skip entries within +-15 min of an event_risk time
and eod holds that span one, (c) bias = keep only the side Newsie favoured (inverse ETFs = short).
Also reported (descriptive, the coach's reading): caution = skip the whole day. Shadow only.

  python -m lab.news.shadow <daytrade_trades.csv> <news/calls dir>
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

DESKS = ["orb_vol", "ema_vol", "volspike", "ema_vol_v2"]
UNDER = {"SPY": ("spy", 1), "UPRO": ("spy", 1), "SPXU": ("spy", -1),
         "QQQ": ("qqq", 1), "TQQQ": ("qqq", 1), "SQQQ": ("qqq", -1)}
TIME = re.compile(r"\b(\d{1,2}):(\d{2})\s*ET\b")


def event_times(day: str, items: list) -> list[datetime]:
    out = []
    for it in items or []:
        txt = it if isinstance(it, str) else json.dumps(it)
        if "already out" in txt or re.search(r"\bclose[ds]?\b", txt):
            continue
        for h, m in TIME.findall(txt):
            h, m = int(h), int(m)
            if 9 * 60 + 30 <= h * 60 + m <= 16 * 60:
                out.append(datetime.fromisoformat(f"{day}T{h:02d}:{m:02d}:00"))
    return sorted(set(out))


def run(trades_csv: Path, calls_dir: Path) -> dict:
    t = pd.read_csv(trades_csv)
    t["day"] = t.entry_t.str[:10]
    t["et_in"] = pd.to_datetime(t.entry_t.str[:19])
    t["et_out"] = pd.to_datetime(t.exit_t.str[:19])
    res = {"days": [], "per_desk": {d: {"base": 0.0, "sit_out": 0.0, "caution": 0.0, "caution_day": 0.0,
                                        "bias": 0.0, "n": 0} for d in DESKS}}
    for f in sorted(calls_dir.glob("20*.json")):
        day = f.stem
        nc = json.loads(f.read_text())
        flags = {x.get("desk"): x.get("flag") for x in nc.get("desk_flags") or []}
        ev = event_times(day, nc.get("event_risk"))
        mr = nc.get("market_read") or {}
        bias = {k: (mr.get(f"{k}_bias") or {}).get("direction") for k in ("spy", "qqq")}
        res["days"].append({"day": day, "flags": flags, "events": [e.strftime("%H:%M") for e in ev], "bias": bias})
        for r in t[(t.day == day) & t.desk.isin(DESKS)].itertuples():
            p = res["per_desk"][r.desk]
            p["n"] += 1
            p["base"] += r.pnl_usd
            fl = flags.get(r.desk)
            if fl != "sit_out":
                p["sit_out"] += r.pnl_usd
            near = any(abs((r.et_in - e).total_seconds()) <= 900 or (r.et_in < e < r.et_out) for e in ev)
            if not (fl in ("caution", "sit_out") and near) and fl != "sit_out":
                p["caution"] += r.pnl_usd
            if fl not in ("caution", "sit_out"):
                p["caution_day"] += r.pnl_usd
            u, side = UNDER[r.sym]
            want = {"up": 1, "down": -1}.get(bias.get(u))
            if want is None or want == side:
                p["bias"] += r.pnl_usd
    for p in res["per_desk"].values():
        for k in ("base", "sit_out", "caution", "caution_day", "bias"):
            p[k] = round(p[k], 2)
    return res


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2])), indent=1))
