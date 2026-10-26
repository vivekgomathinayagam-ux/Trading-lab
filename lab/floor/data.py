"""US ETF bars from Yahoo Finance's public chart API (no key). Runs on GitHub Actions
(Claude's workspace can't reach it).

Limits (Yahoo): 1-minute bars only for the last ~30 days, max 8 days per request;
5-minute for the last 60 days; daily for the full history. So the lab ARCHIVES
1-minute bars (gzip CSV, one file per symbol) and every run merges new bars in;
the archive lives on branch `data` under backtests/data/etf1m/ and grows daily.
"""
from __future__ import annotations

import csv
import gzip
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from strategies.daytrade.core import Bar

NY = ZoneInfo("America/New_York")
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
UA = {"User-Agent": "Mozilla/5.0 (compound-city-lab; research backtests)"}


def _get(sym: str, params: dict, tries: int = 6) -> dict:
    wait = 2.0
    for attempt in range(tries):
        try:
            r = requests.get(CHART.format(sym=sym), params=params, headers=UA, timeout=30)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"status {r.status_code}")
            r.raise_for_status()
            res = r.json()["chart"]["result"]
            return res[0] if res else {}
        except (requests.RequestException, ValueError, KeyError, TypeError):
            if attempt == tries - 1:
                raise
            time.sleep(wait)
            wait = min(wait * 2, 60)
    return {}


def _parse(res: dict, regular_only: bool = True) -> list[Bar]:
    ts = res.get("timestamp") or []
    q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
    out = []
    for i, t in enumerate(ts):
        try:
            o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        except (KeyError, IndexError):
            continue
        if None in (o, h, l, c) or min(o, h, l, c) <= 0:
            continue
        dt = datetime.fromtimestamp(t, timezone.utc).astimezone(NY)
        if regular_only and not (dtime_ok(dt)):
            continue
        out.append(Bar(dt, float(o), float(max(h, o, c)), float(min(l, o, c)), float(c), float(v or 0)))
    return out


def dtime_ok(dt: datetime) -> bool:
    m = dt.hour * 60 + dt.minute
    return dt.weekday() < 5 and 570 <= m < 960


def fetch_intraday(sym: str, interval: str = "1m", days: int = 29, pause: float = 0.6) -> list[Bar]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    step = timedelta(days=7 if interval == "1m" else 59)
    bars: dict[datetime, Bar] = {}
    t = start
    while t < end:
        t2 = min(t + step, end)
        res = _get(sym, {"interval": interval, "period1": int(t.timestamp()), "period2": int(t2.timestamp()),
                         "includePrePost": "false", "events": "history"})
        for b in _parse(res):
            bars[b.t] = b
        t = t2
        time.sleep(pause)
    return [bars[k] for k in sorted(bars)]


def fetch_daily(sym: str, start: str = "2010-03-01") -> list[tuple]:
    p1 = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
    res = _get(sym, {"interval": "1d", "period1": p1, "period2": int(time.time()), "events": "history"})
    ts = res.get("timestamp") or []
    q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
    rows = []
    for i, t in enumerate(ts):
        o, h, l, c = (q.get(k, [None] * len(ts))[i] for k in ("open", "high", "low", "close"))
        if None in (o, h, l, c) or o <= 0:
            continue
        rows.append((datetime.fromtimestamp(t, timezone.utc).date().isoformat(), o, h, l, c))
    return rows


# ---------------------------------------------------------------- archive
def load_archive(path: Path) -> dict[datetime, Bar]:
    out: dict[datetime, Bar] = {}
    if not path.exists():
        return out
    with gzip.open(path, "rt", newline="") as f:
        for row in csv.DictReader(f):
            t = datetime.fromisoformat(row["t"]).astimezone(NY)
            out[t] = Bar(t, float(row["o"]), float(row["h"]), float(row["l"]), float(row["c"]), float(row["v"]))
    return out


def save_archive(path: Path, bars: dict[datetime, Bar]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "o", "h", "l", "c", "v"])
        for k in sorted(bars):
            b = bars[k]
            w.writerow([b.t.isoformat(), b.o, b.h, b.l, b.c, int(b.v)])


def load_1m(sym: str, archive_dir: Path, fetch: bool = True) -> list[Bar]:
    path = archive_dir / f"{sym}.csv.gz"
    have = load_archive(path)
    if fetch:
        for b in fetch_intraday(sym, "1m", 29):
            have[b.t] = b
        save_archive(path, have)
    return [have[k] for k in sorted(have)]
