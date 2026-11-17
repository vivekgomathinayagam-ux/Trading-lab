"""Grow a long 5-minute archive (SPY, QQQ, ...) from Alpaca's historical stock bars (research only).

Keys come from the environment (GitHub Actions secrets ALPACA_KEY_ID / ALPACA_SECRET_KEY); they
are never printed or written. Free plan: SIP history older than 15 minutes, IEX as the fallback.
Usage: python -m lab.foundry.fetch_alpaca <archive dir> SPY,QQQ [start YYYY-MM-DD]
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from lab.floor.data import load_archive, save_archive
from strategies.daytrade.core import Bar

URL = "https://data.alpaca.markets/v2/stocks/bars"
NY = ZoneInfo("America/New_York")


def parse_bars(payload: dict, sym: str) -> list[Bar]:
    out = []
    for r in (payload.get("bars") or {}).get(sym, []) or []:
        t = datetime.fromisoformat(r["t"].replace("Z", "+00:00")).astimezone(NY)
        if 570 <= t.hour * 60 + t.minute < 960 and t.weekday() < 5:      # regular hours only
            out.append(Bar(t, float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]), float(r["v"])))
    return out


def fetch(sym: str, start: str, end: str, feed: str, headers: dict, session=requests) -> list[Bar]:
    bars, token = [], None
    while True:
        p = {"symbols": sym, "timeframe": "5Min", "start": start, "end": end, "limit": 10000,
             "adjustment": "raw", "feed": feed, "sort": "asc"}
        if token:
            p["page_token"] = token
        r = session.get(URL, params=p, headers=headers, timeout=60)
        if r.status_code == 429:
            time.sleep(5)
            continue
        r.raise_for_status()
        j = r.json()
        bars += parse_bars(j, sym)
        token = j.get("next_page_token")
        if not token:
            return bars


def main(argv: list[str]) -> int:
    out, syms = Path(argv[1]), argv[2].split(",")
    start = argv[3] if len(argv) > 3 else "2020-01-01"
    headers = {"APCA-API-KEY-ID": os.environ.get("ALPACA_KEY_ID", ""),
               "APCA-API-SECRET-KEY": os.environ.get("ALPACA_SECRET_KEY", "")}
    if not headers["APCA-API-KEY-ID"]:
        print("ALPACA_KEY_ID not set: skipping (add the GitHub secrets)")
        return 0
    end = (datetime.now(timezone.utc) - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out.mkdir(parents=True, exist_ok=True)
    for sym in syms:
        path = out / f"{sym}.csv.gz"
        have = load_archive(path) if path.exists() else {}
        s = (max(have) - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00Z") if have else f"{start}T00:00:00Z"
        try:
            new = fetch(sym, s, end, "sip", headers)
        except requests.HTTPError as e:                     # free plan or entitlement: fall back to IEX
            print(sym, "sip failed", e.response.status_code, "-> iex")
            new = fetch(sym, s, end, "iex", headers)
        for b in new:
            have[b.t] = b
        save_archive(path, have)
        days = len({t.date() for t in have})
        print(sym, len(have), "bars,", days, "sessions,", min(have).date(), "to", max(have).date())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
