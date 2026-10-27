"""Read-only price checks for the day-trade desks (approved by Vivek 2026-10-26).

SkylitSpot asks Skylit's REST API for the current spot price of several symbols
in one call:  GET https://api.skylit.ai/v1/gex/levels?symbols=A,B,...
with header  Authorization: Bearer <SKYLIT_API_KEY>  (1 credit per call).

It is used for two things only:
  * an independent cross-check of the Yahoo price at every simulated fill, and
  * valuing open positions when Yahoo fails (no new entries are opened then).
It never places, changes or prices an order in normal operation.
The key comes only from the Railway variable SKYLIT_API_KEY and is never logged.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

log = logging.getLogger("quotecheck")
LEVELS = "https://api.skylit.ai/v1/gex/levels"
STALE_QUOTE_S = 90          # Vivek: flag quotes older than 90 seconds
XCHECK_FLAG_PCT = 0.05      # Vivek: flag Yahoo vs Skylit differences above 0.05%


class SkylitSpot:
    def __init__(self, api_key: str | None, timeout: int = 6):
        self.key = api_key
        self.timeout = timeout
        self.s = requests.Session()
        self.status = "unconfigured" if not api_key else "unknown"

    @property
    def configured(self) -> bool:
        return bool(self.key)

    def spots(self, symbols: list[str]) -> dict[str, dict]:
        """{symbol: {"spot": float, "as_of": iso str}}. Empty dict on any failure."""
        if not self.key:
            self.status = "unconfigured"
            return {}
        try:
            r = self.s.get(LEVELS, params={"symbols": ",".join(symbols), "max_expirations": 1,
                                           "max_strikes": 1},
                           headers={"Authorization": f"Bearer {self.key}"}, timeout=self.timeout)
            if r.status_code != 200:
                self.status = f"http {r.status_code}"
                log.warning("skylit spot check failed: HTTP %s", r.status_code)
                return {}
            out = {}
            for row in ((r.json().get("data") or {}).get("symbols") or []):
                sym, spot = row.get("symbol"), row.get("spot")
                if sym and spot:
                    out[sym.upper()] = {"spot": float(spot), "as_of": row.get("asOf") or ""}
            self.status = "ok" if out else "empty"
            return out
        except (requests.RequestException, ValueError) as e:
            self.status = "error"
            log.warning("skylit spot check failed: %s", type(e).__name__)
            return {}


def pct_diff(a: float | None, b: float | None) -> float | None:
    if not a or not b:
        return None
    return round((a / b - 1) * 100, 4)


def age_seconds(quote_epoch: float | None, at: datetime) -> float | None:
    if not quote_epoch:
        return None
    return round(at.timestamp() - float(quote_epoch), 1)


def iso_utc(epoch: float | None) -> str:
    if not epoch:
        return ""
    return datetime.fromtimestamp(float(epoch), timezone.utc).isoformat(timespec="seconds")
