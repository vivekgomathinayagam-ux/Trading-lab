"""Live 1-minute bars for the day-trade desks (Yahoo Finance chart API, no key).

Only COMPLETED bars are returned (a bar is complete once its minute has ended),
so the desks never act on a half-formed bar. The latest trade price comes back
too, for shadow fills. Regular hours only (09:30-16:00 ET).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

from strategies.daytrade.core import Bar

log = logging.getLogger("marketdata")
NY = ZoneInfo("America/New_York")
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
UA = {"User-Agent": "Mozilla/5.0 (compound-city-bot)"}


class YahooBars:
    def __init__(self, timeout: int = 10):
        self.s = requests.Session()
        self.s.headers.update(UA)
        self.timeout = timeout
        # Provenance of the latest price per symbol (logging only, never used to trade):
        # quote_epoch = Yahoo's regularMarketTime, delayed_by = exchangeDataDelayedBy (minutes),
        # fetched_at = when the bot received it.
        self.last_meta: dict[str, dict] = {}

    def bars(self, sym: str, rng: str = "1d", now: datetime | None = None) -> tuple[list[Bar], float | None]:
        r = self.s.get(CHART.format(sym=sym), params={"interval": "1m", "range": rng, "includePrePost": "false"},
                       timeout=self.timeout)
        r.raise_for_status()
        res = (r.json().get("chart") or {}).get("result") or []
        if not res:
            return [], None
        res = res[0]
        meta = res.get("meta") or {}
        price = meta.get("regularMarketPrice")
        self.last_meta[sym] = {"quote_epoch": meta.get("regularMarketTime"),
                               "delayed_by": meta.get("exchangeDataDelayedBy"),
                               "fetched_at": datetime.now(timezone.utc)}
        now = now or datetime.now(timezone.utc)
        ts = res.get("timestamp") or []
        q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
        out = []
        for i, t in enumerate(ts):
            try:
                o, h, l, c, v = (q[k][i] for k in ("open", "high", "low", "close", "volume"))
            except (KeyError, IndexError, TypeError):
                continue
            if None in (o, h, l, c) or min(o, h, l, c) <= 0:
                continue
            dt = datetime.fromtimestamp(t, timezone.utc)
            if dt + timedelta(seconds=60) > now - timedelta(seconds=2):   # minute not finished yet
                continue
            et = dt.astimezone(NY)
            m = et.hour * 60 + et.minute
            if et.weekday() >= 5 or not (570 <= m < 960):
                continue
            out.append(Bar(et, float(o), float(max(h, o, c)), float(min(l, o, c)), float(c), float(v or 0)))
        return out, (float(price) if price else None)
