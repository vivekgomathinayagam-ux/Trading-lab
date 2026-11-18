"""Measure real bid/ask spreads (bps of mid) per ticker and time-of-day bucket from Alpaca SIP quotes (research only).
Usage: python -m lab.scalp.fetch_spreads out.json SYM1,SYM2,...
Samples 8 sessions spread over the last 10 months, 3 buckets (open 09:50, midday 12:00, late 15:00 ET), first 1000 quotes after each time."""
from __future__ import annotations
import json, os, statistics, sys, time
from datetime import date, timedelta
import requests

URL = "https://data.alpaca.markets/v2/stocks/quotes"
H = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""), "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "")}
BUCKETS = {"open": (14, 50), "mid": (17, 0), "late": (20, 0)}      # UTC (ET+5 in winter; sampled days are all standard time)


def sample_days(n=8) -> list[str]:
    out, d = [], date(2026, 11, 13)
    step = 30
    while len(out) < n:
        x = d
        while x.weekday() >= 5:
            x -= timedelta(days=1)
        if not (date(2026, 3, 8) <= x < date(2026, 11, 1)):          # keep to standard time (UTC-5): Nov-Mar
            out.append(x.isoformat())
        d -= timedelta(days=step)
    return out


def spread_bps(sym: str, day: str, hh: int, mm: int) -> list[float]:
    p = {"symbols": sym, "start": f"{day}T{hh:02d}:{mm:02d}:00Z", "end": f"{day}T{hh:02d}:{mm + 5:02d}:00Z",
         "limit": 1000, "feed": "sip"}
    for _ in range(4):
        r = requests.get(URL, params=p, headers=H, timeout=60)
        if r.status_code == 429:
            time.sleep(5); continue
        if not r.ok:
            return []
        qs = (r.json().get("quotes") or {}).get(sym, [])
        return [(q["ap"] - q["bp"]) / ((q["ap"] + q["bp"]) / 2) * 1e4 for q in qs if q["bp"] > 0 and q["ap"] >= q["bp"]]
    return []


def main(out: str, syms: list[str]) -> None:
    res = {}
    days = [d for d in sample_days(12)][:8]
    for s in syms:
        res[s] = {}
        for name, (hh, mm) in BUCKETS.items():
            v = [x for d in days for x in spread_bps(s, d, hh, mm)]
            res[s][name] = round(statistics.median(v), 2) if v else None
        print(s, res[s], flush=True)
    with open(out, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2].split(","))
