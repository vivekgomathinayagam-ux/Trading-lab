"""One broker interface. Tradier sandbox, Tradier live and (later) Robinhood
alert-mode all sit behind it, so a setup can be switched by config."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from engine.risk import Order


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    ts: str              # ISO-8601 UTC
    source: str          # "tradier_sandbox" | "tradier_live" | "yahoo_rt"
    delayed: bool


@dataclass
class Balances:
    equity: float
    cash: float
    settled_cash: float
    buying_power: float
    raw: dict


@dataclass
class OrderResult:
    ok: bool
    order_id: Optional[str]
    status: str
    raw: dict


class Broker(ABC):
    name: str = "base"
    is_paper: bool = True

    @abstractmethod
    def ping(self) -> dict: ...

    @abstractmethod
    def balances(self) -> Balances: ...

    @abstractmethod
    def quote(self, symbol: str) -> Quote: ...

    @abstractmethod
    def place(self, order: Order, preview: bool = False) -> OrderResult: ...

    @abstractmethod
    def positions(self) -> list[dict]: ...
