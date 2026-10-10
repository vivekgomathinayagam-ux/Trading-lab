"""Ledger writer: every order, fill, shadow fill, hustle payment and cost as
one CSV row. Append-only. Files live in /ledger and are pushed to the "data"
branch by engine/datapush.py.

Files:
  ledger/trades.csv     orders + fills + shadow fills
  ledger/money.csv      hustle income, costs, deposits (the $50 seed)
  ledger/heartbeat.json last bot heartbeat (overwritten)
  ledger/snapshot.json  latest balances/positions/status (overwritten)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
from pathlib import Path

TRADE_COLS = ["ts", "event", "mode", "strategy", "symbol", "side", "qty", "price",
              "source", "order_id", "max_loss", "cost", "note"]
MONEY_COLS = ["ts", "kind", "amount", "currency", "counterparty", "category", "note"]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, root: str = "ledger"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.trades = self.root / "trades.csv"
        self.money = self.root / "money.csv"
        self._ensure(self.trades, TRADE_COLS)
        self._ensure(self.money, MONEY_COLS)

    @staticmethod
    def _ensure(path: Path, cols: list[str]) -> None:
        if not path.exists() or path.stat().st_size == 0:
            with path.open("w", newline="") as f:
                csv.writer(f).writerow(cols)

    def _append(self, path: Path, cols: list[str], row: dict) -> dict:
        row = {c: row.get(c, "") for c in cols}
        row["ts"] = row["ts"] or _now()
        with path.open("a", newline="") as f:
            csv.DictWriter(f, fieldnames=cols).writerow(row)
        return row

    # ----- trades --------------------------------------------------------
    def trade(self, event: str, mode: str, strategy: str, symbol: str, side: str,
              qty: float, price: float | None = None, source: str = "", order_id: str = "",
              max_loss: float | None = None, cost: float | None = None, note: str = "") -> dict:
        return self._append(self.trades, TRADE_COLS, dict(
            event=event, mode=mode, strategy=strategy, symbol=symbol, side=side, qty=qty,
            price="" if price is None else price, source=source, order_id=order_id,
            max_loss="" if max_loss is None else max_loss, cost="" if cost is None else cost,
            note=note))

    # ----- money ---------------------------------------------------------
    def money_row(self, kind: str, amount: float, category: str, counterparty: str = "",
                  note: str = "", currency: str = "USD") -> dict:
        return self._append(self.money, MONEY_COLS, dict(
            kind=kind, amount=amount, currency=currency, counterparty=counterparty,
            category=category, note=note))

    # ----- json state ----------------------------------------------------
    def write_json(self, name: str, data: dict) -> Path:
        p = self.root / name
        data = {"as_of": _now(), **data}
        p.write_text(json.dumps(data, indent=2, default=str))
        return p

    def heartbeat(self, status: str, extra: dict | None = None) -> Path:
        return self.write_json("heartbeat.json", {"status": status, **(extra or {})})

    def read_rows(self, which: str = "trades") -> list[dict]:
        p = self.trades if which == "trades" else self.money
        with p.open() as f:
            return list(csv.DictReader(f))
