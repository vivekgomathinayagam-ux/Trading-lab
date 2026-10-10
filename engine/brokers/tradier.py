"""Tradier adapter (sandbox = paper). Plain REST, no SDK.

Sandbox facts that matter (docs.tradier.com FAQ): quotes and fills are delayed
~15 minutes and there is no streaming. So every intraday setup also records a
shadow fill from a real-time source (see engine/shadow.py).

Live orders: `place()` refuses to send unless the adapter was built with the
live token AND settings.mode == "live". The risk engine is checked by the
caller before this is ever reached; this is a second lock, not the first.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

import requests

from engine.brokers.base import Balances, Broker, OrderResult, Quote
from engine.risk import Order

log = logging.getLogger("tradier")

SANDBOX_URL = "https://sandbox.tradier.com/v1"
LIVE_URL = "https://api.tradier.com/v1"


class TradierBroker(Broker):
    def __init__(self, token: str, live: bool = False, account_id: Optional[str] = None,
                 timeout: int = 15):
        if not token:
            raise ValueError("Tradier token missing")
        self.live = live
        self.is_paper = not live
        self.name = "tradier_live" if live else "tradier_sandbox"
        self.base = LIVE_URL if live else SANDBOX_URL
        self.timeout = timeout
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}",
                               "Accept": "application/json"})
        self.account_id = account_id or self._discover_account()

    # ----- http ----------------------------------------------------------
    def _get(self, path: str, **params) -> dict:
        r = self.s.get(f"{self.base}{path}", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _post(self, path: str, data: dict) -> dict:
        r = self.s.post(f"{self.base}{path}", data=data, timeout=self.timeout)
        r.raise_for_status()
        return r.json() if r.text else {}

    # ----- account -------------------------------------------------------
    def _discover_account(self) -> Optional[str]:
        try:
            prof = self._get("/user/profile")
            acct = prof["profile"]["account"]
            if isinstance(acct, list):
                acct = acct[0]
            return acct["account_number"]
        except Exception as e:  # noqa: BLE001
            log.warning("could not discover account id: %s", e)
            return None

    def ping(self) -> dict:
        prof = self._get("/user/profile")
        acct = prof["profile"]["account"]
        if isinstance(acct, list):
            acct = acct[0]
        return {"account_number": acct.get("account_number"),
                "type": acct.get("type"), "status": acct.get("status"),
                "classification": acct.get("classification"), "paper": self.is_paper}

    def balances(self) -> Balances:
        b = self._get(f"/accounts/{self.account_id}/balances")["balances"]
        cash = b.get("cash") or {}
        settled = (cash.get("cash_available") if isinstance(cash, dict) else None)
        if settled is None:
            settled = b.get("total_cash", 0.0)
        return Balances(equity=float(b.get("total_equity") or 0.0),
                        cash=float(b.get("total_cash") or 0.0),
                        settled_cash=float(settled or 0.0),
                        buying_power=float((cash.get("cash_available") if isinstance(cash, dict) else 0) or 0.0),
                        raw=b)

    def positions(self) -> list[dict]:
        p = self._get(f"/accounts/{self.account_id}/positions").get("positions")
        if not p or p == "null":
            return []
        pos = p.get("position", [])
        return pos if isinstance(pos, list) else [pos]

    # ----- market data ---------------------------------------------------
    def quote(self, symbol: str) -> Quote:
        q = self._get("/markets/quotes", symbols=symbol, greeks="false")["quotes"]["quote"]
        if isinstance(q, list):
            q = q[0]
        return Quote(symbol=symbol, bid=float(q.get("bid") or 0), ask=float(q.get("ask") or 0),
                     last=float(q.get("last") or 0),
                     ts=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                     source=self.name, delayed=self.is_paper)

    def expirations(self, symbol: str) -> list[str]:
        e = self._get("/markets/options/expirations", symbol=symbol, includeAllRoots="true")
        exp = (e.get("expirations") or {}).get("date") or []
        return exp if isinstance(exp, list) else [exp]

    def clock(self) -> dict:
        return self._get("/markets/clock").get("clock", {})

    # ----- orders --------------------------------------------------------
    def place(self, order: Order, preview: bool = False) -> OrderResult:
        if order.mode == "live" and not self.live:
            return OrderResult(False, None, "refused: live order on paper adapter", {})
        if self.live and order.mode != "live":
            return OrderResult(False, None, "refused: paper order on live adapter", {})
        data = self._to_tradier(order)
        if preview:
            data["preview"] = "true"
        res = self._post(f"/accounts/{self.account_id}/orders", data)
        o = res.get("order", {})
        ok = (o.get("status") in ("ok", "open", "filled", "pending")) or bool(o.get("id"))
        return OrderResult(ok=ok, order_id=str(o.get("id")) if o.get("id") else None,
                           status=str(o.get("status", res)), raw=res)

    @staticmethod
    def _to_tradier(order: Order) -> dict:
        if order.asset_type == "equity":
            return {"class": "equity", "symbol": order.symbol, "side": order.side,
                    "quantity": str(int(order.qty)), "type": "market", "duration": "day"}
        if order.asset_type == "option" and len(order.legs) == 1:
            leg = order.legs[0]
            return {"class": "option", "symbol": order.symbol, "option_symbol": leg.symbol,
                    "side": leg.side, "quantity": str(int(leg.qty)), "type": "market",
                    "duration": "day"}
        data = {"class": "multileg", "symbol": order.symbol, "type": "market", "duration": "day"}
        for i, leg in enumerate(order.legs):
            data[f"option_symbol[{i}]"] = leg.symbol
            data[f"side[{i}]"] = leg.side
            data[f"quantity[{i}]"] = str(int(leg.qty))
        return data
