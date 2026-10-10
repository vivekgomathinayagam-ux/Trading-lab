"""Market-hours helpers (US equities, America/New_York)."""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
LA = ZoneInfo("America/Los_Angeles")
OPEN = dt.time(9, 30)
CLOSE = dt.time(16, 0)


def now_ny() -> dt.datetime:
    return dt.datetime.now(NY)


def is_market_hours(t: dt.datetime | None = None) -> bool:
    t = t or now_ny()
    return t.weekday() < 5 and OPEN <= t.time() < CLOSE


def is_close_window(t: dt.datetime | None = None, minutes: int = 2) -> bool:
    """True during the first `minutes` after the close."""
    t = t or now_ny()
    if t.weekday() >= 5:
        return False
    close = t.replace(hour=16, minute=0, second=0, microsecond=0)
    return close <= t < close + dt.timedelta(minutes=minutes)
