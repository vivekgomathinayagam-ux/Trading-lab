"""Alpaca PAPER adapter (approved by Vivek 2026-11-17). Paper only, by construction:

- The trading base URL is the paper endpoint and cannot be changed: the constructor refuses any
  other URL, and there is no live flag. Alpaca's live endpoint (api.alpaca.markets) is never used.
- place() refuses any order whose mode is not "paper", and anything but whole-share equities.
- Every order carries a client_order_id, so a retry can't create a duplicate (Alpaca rejects a
  repeated id).
- Entries are marketable limits (limit = ask x (1 + max_slip)); never blind market orders.

Keys come from Railway variables ALPACA_KEY_ID / ALPACA_SECRET_KEY (typed by Vivek); never logged.
Quotes come from the IEX feed (real time on the free plan; a partial book, so spreads read wide).
"""
from __future__ import annotations

import datetime as dt
import logging
import uuid
from typing import Optional

import requests

from engine.brokers.base import Balances, Broker, OrderResult, Quote
from engine.risk import Order

log = logging.getLogger("alpaca_paper")

PAPER_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"
LIVE_URL_FORBIDDEN = "https://api.alpaca.markets"


class AlpacaPaperBroker(Broker):
    name = "alpaca_paper"
    is_paper = True

    def __init__(self, key_id: str, secret: str, base_url: str = PAPER_URL, timeout: int = 10,
                 session=None):
        if base_url.rstrip("/") != PAPER_URL:
            raise ValueError("AlpacaPaperBroker only talks to the paper endpoint")
        if not key_id or not secret:
            raise ValueError("Alpaca keys missing")
        self.base, self.timeout = PAPER_URL, timeout
        self.s = session or requests.Session()
        self.s.headers.update({"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret})

    # ----- http (every call is pinned to the paper or data host) ----------
    def _url(self, host: str, path: str) -> str:
        assert host in (PAPER_URL, DATA_URL), "unexpected host"
        return f"{host}{path}"

    def _get(self, host: str, path: str, **params) -> dict | list:
        r = self.s.get(self._url(host, path), params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _send(self, method: str, path: str, json: Optional[dict] = None) -> dict | list:
        r = self.s.request(method, self._url(PAPER_URL, path), json=json, timeout=self.timeout)
        if r.status_code >= 400:
            return {"_error": r.status_code, "message": (r.text or "")[:200]}
        return r.json() if r.text else {}

    # ----- account ---------------------------------------------------------
    def ping(self) -> dict:
        a = self._get(PAPER_URL, "/v2/account")
        return {"status": a.get("status"), "paper": True, "currency": a.get("currency"),
                "pattern_day_trader": a.get("pattern_day_trader")}

    def balances(self) -> Balances:
        a = self._get(PAPER_URL, "/v2/account")
        return Balances(equity=float(a.get("equity") or 0), cash=float(a.get("cash") or 0),
                        settled_cash=float(a.get("cash") or 0),
                        buying_power=float(a.get("non_marginable_buying_power") or a.get("cash") or 0),
                        raw=a)

    def positions(self) -> list[dict]:
        return list(self._get(PAPER_URL, "/v2/positions") or [])

    def open_orders(self) -> list[dict]:
        return list(self._get(PAPER_URL, "/v2/orders", status="open") or [])

    def get_order(self, order_id: str) -> dict:
        return self._get(PAPER_URL, f"/v2/orders/{order_id}")

    # ----- market data -----------------------------------------------------
    def quote(self, symbol: str) -> Quote:
        q = self._get(DATA_URL, "/v2/stocks/quotes/latest", symbols=symbol, feed="iex")
        q = (q.get("quotes") or {}).get(symbol) or {}
        bid, ask = float(q.get("bp") or 0), float(q.get("ap") or 0)
        return Quote(symbol=symbol, bid=bid, ask=ask, last=(bid + ask) / 2 if bid and ask else 0.0,
                     ts=q.get("t") or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                     source="alpaca_iex", delayed=False)

    # ----- orders ----------------------------------------------------------
    def place(self, order: Order, preview: bool = False, limit_px: Optional[float] = None,
              client_order_id: Optional[str] = None) -> OrderResult:
        if order.mode != "paper":
            return OrderResult(False, None, "refused: not a paper order", {})
        if order.asset_type != "equity" or order.legs or order.uses_margin:
            return OrderResult(False, None, "refused: whole-share equities only", {})
        qty = int(order.qty)
        if qty < 1 or qty != order.qty:
            return OrderResult(False, None, "refused: whole shares only", {})
        cid = client_order_id or f"{order.strategy}-{uuid.uuid4().hex[:16]}"
        body = {"symbol": order.symbol, "qty": str(qty), "side": order.side,
                "time_in_force": "day", "client_order_id": cid}
        if limit_px:
            body.update({"type": "limit", "limit_price": f"{limit_px:.2f}"})
        else:
            body["type"] = "market"            # exits only; entries pass limit_px
        if preview:
            return OrderResult(True, None, "preview", body)
        res = self._send("POST", "/v2/orders", body)
        if isinstance(res, dict) and res.get("_error"):
            log.warning("order rejected %s: %s", res["_error"], res.get("message"))
            return OrderResult(False, None, f"rejected {res['_error']}", res)
        return OrderResult(True, str(res.get("id")), str(res.get("status")), res)

    def cancel(self, order_id: str) -> bool:
        res = self._send("DELETE", f"/v2/orders/{order_id}")
        return not (isinstance(res, dict) and res.get("_error"))

    def flatten_all(self) -> dict:
        """Emergency: cancel every open order and close every position (paper account only)."""
        return {"cancel": self._send("DELETE", "/v2/orders"),
                "close": self._send("DELETE", "/v2/positions")}
