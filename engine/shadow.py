"""Shadow-fill simulator.

Tradier's sandbox fills at ~15-minute-delayed prices, which makes intraday
setups (ORB, 3-min CVD, 0DTE) look wrong. So for every paper order we also
record a *shadow fill*: the price a real-time source showed at the moment the
signal fired, worse by a fixed slippage so results are conservative.

Real-time source: Yahoo Finance's public 1-minute chart endpoint. It gives
last-trade price (not bid/ask) and is real-time for most US ETFs. Known
limits, logged honestly: no bid/ask, occasional 60-120s lag, can rate-limit.
If a better read-only real-time source is added later (e.g. a market-data-only
Tradier token), only `RealtimeQuotes` changes.

Option shadow fills: the real-time source has no option quotes. For options we
shadow-price from the sandbox chain's bid/ask (delayed) and flag the fill as
"option_delayed". That is a known gap until a real options feed exists.
"""
from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass

import requests

from engine.brokers.base import Quote
from engine.risk import Order

log = logging.getLogger("shadow")

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
UA = {"User-Agent": "Mozilla/5.0 (compound-city-bot)"}


class RealtimeQuotes:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.s = requests.Session()
        self.s.headers.update(UA)

    def quote(self, symbol: str) -> Quote:
        r = self.s.get(YAHOO_CHART.format(sym=symbol),
                       params={"interval": "1m", "range": "1d", "includePrePost": "false"},
                       timeout=self.timeout)
        r.raise_for_status()
        res = r.json()["chart"]["result"][0]
        meta = res["meta"]
        last = float(meta.get("regularMarketPrice") or 0)
        ts = meta.get("regularMarketTime")
        iso = (dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec="seconds")
               if ts else dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        return Quote(symbol=symbol, bid=last, ask=last, last=last, ts=iso,
                     source="yahoo_rt", delayed=False)


@dataclass
class ShadowFill:
    symbol: str
    side: str
    qty: float
    price: float
    ts: str
    source: str
    slippage_bps: float
    note: str


class ShadowSimulator:
    def __init__(self, rt: RealtimeQuotes | None = None, slippage_bps: float = 2.0):
        self.rt = rt or RealtimeQuotes()
        self.slippage_bps = slippage_bps

    @staticmethod
    def apply_slippage(price: float, side: str, bps: float) -> float:
        """Buys fill higher, sells fill lower."""
        adj = price * bps / 10_000
        return round(price + adj, 4) if side.startswith("buy") else round(price - adj, 4)

    def fill(self, order: Order, option_quote: Quote | None = None) -> ShadowFill | None:
        try:
            if order.asset_type == "equity":
                q = self.rt.quote(order.symbol)
                px = self.apply_slippage(q.last, order.side, self.slippage_bps)
                return ShadowFill(order.symbol, order.side, order.qty, px, q.ts, q.source,
                                  self.slippage_bps, "rt_last_plus_slippage")
            if option_quote is not None:
                # options: buy at ask, sell at bid (conservative), delayed source
                px = option_quote.ask if order.side.startswith("buy") else option_quote.bid
                return ShadowFill(option_quote.symbol, order.side, order.qty, px,
                                  option_quote.ts, option_quote.source, 0.0, "option_delayed")
            return None
        except Exception as e:  # noqa: BLE001
            log.warning("shadow fill failed for %s: %s", order.symbol, e)
            return None
