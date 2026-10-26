"""Runs the day-trade desks (strategies/daytrade/core.py) inside the Railway bot, on paper.

Each desk is its own virtual $1,000 book (results compound per desk). On every new
completed 1-minute bar, in the same order as the backtest lab:
  exits (stop / target / 15:55) -> features update -> entry signal.
Entries and exits are priced at the live Yahoo price plus the lab's slippage
("shadow fills", the official result), and also sent to the Tradier sandbox as
paper orders (delayed fills, logged for plumbing only). Paper only: this runner
never builds a live order, and every entry passes the risk engine.

Files (pushed to branch data with the rest of /ledger):
  ledger/daytrade_books.json   desk cash/positions, per-desk peak and start of day, SPY benchmark
  ledger/daytrade_trades.csv   one row per closed trade
"""
from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, time as dtime, timedelta
from pathlib import Path

import yaml

from engine.risk import AccountState, Order, RiskEngine
from strategies.daytrade.core import (PAPER_RULES, SLIP, STOP_PCT, SYMBOLS, Bar, Desk,
                                      Features)

log = logging.getLogger("daytrade")
CONFIG = Path(__file__).resolve().parent.parent / "strategies" / "daytrade" / "config.yaml"
SAFETY_FLAT = dtime(15, 58)
TRADE_COLS = ["desk", "sym", "qty", "entry_t", "exit_t", "entry_px", "exit_px", "pnl_usd",
              "pnl_pct_equity", "move_pct", "reason", "equity_after"]


def enabled() -> bool:
    try:
        return (yaml.safe_load(CONFIG.read_text()) or {}).get("stage") in ("paper",)
    except Exception:  # noqa: BLE001
        return False


class DayTradeRunner:
    def __init__(self, ledger, broker, risk: RiskEngine, md, ledger_dir: Path,
                 equity: float = 1000.0, symbols=None, rules=None):
        self.ledger, self.broker, self.risk, self.md = ledger, broker, risk, md
        self.symbols = list(symbols or SYMBOLS)
        self.order = {s: i for i, s in enumerate(self.symbols)}
        self.hub = {s: Features() for s in self.symbols}
        self.desks = {r.key: Desk(rule=r, cash=equity, start_equity=equity) for r in (rules or PAPER_RULES)}
        self.last_t: dict[str, datetime | None] = {s: None for s in self.symbols}
        self.meta: dict = {"peak": {}, "sod": {}, "sod_date": None, "benchmark": {}, "started": None}
        self.books_path = ledger_dir / "daytrade_books.json"
        self.trades_path = ledger_dir / "daytrade_trades.csv"
        self.warmed = False
        self.load()

    # ---------------------------------------------------------- persistence
    def load(self) -> None:
        if not self.books_path.exists():
            return
        try:
            d = json.loads(self.books_path.read_text())
        except (OSError, ValueError):
            log.error("daytrade_books.json unreadable; starting fresh books")
            return
        for k, v in (d.get("desks") or {}).items():
            if k in self.desks:
                self.desks[k].load(v)
        for k in ("peak", "sod", "sod_date", "benchmark", "started"):
            if k in d:
                self.meta[k] = d[k]

    def save(self, marks: dict | None = None) -> None:
        out = {"as_of": datetime.now().astimezone().isoformat(timespec="seconds"), **self.meta,
               "marks": {k: round(v, 4) for k, v in (marks or {}).items()},
               "desks": {k: {**d.to_dict(), "label": d.rule.label, "equity": round(d.equity(marks), 2)}
                         for k, d in self.desks.items()}}
        self.books_path.write_text(json.dumps(out, indent=1))

    def _record(self, tr: dict) -> None:
        new = not self.trades_path.exists()
        with self.trades_path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TRADE_COLS)
            if new:
                w.writeheader()
            w.writerow({k: tr.get(k, "") for k in TRADE_COLS})

    # ---------------------------------------------------------- warm-up
    def warmup(self) -> None:
        """Feed the last 5 sessions of bars into the features only (no trading),
        so volume baselines and EMAs are ready. Desks keep their saved state."""
        for s in self.symbols:
            try:
                bars, _ = self.md.bars(s, "5d")
            except Exception as e:  # noqa: BLE001
                log.warning("warm-up %s failed: %s", s, e)
                continue
            for b in bars:
                self.hub[s].update(b)
                self.last_t[s] = b.t
        self.warmed = True
        log.info("day-trade desks warmed up: %s",
                 {s: (self.last_t[s].isoformat() if self.last_t[s] else None) for s in self.symbols})

    # ---------------------------------------------------------- trading
    def _acct(self, d: Desk) -> AccountState:
        eq = d.equity()
        return AccountState(equity=eq, peak_equity=max(self.meta["peak"].get(d.key, eq), eq),
                            start_of_day_equity=self.meta["sod"].get(d.key, eq),
                            settled_cash=d.cash, mode="paper", live_token_present=False)

    def _paper_order(self, order: Order) -> str:
        try:
            res = self.broker.place(order)
            return f"sandbox {res.status} {res.order_id or ''}".strip()
        except Exception as e:  # noqa: BLE001
            return f"sandbox order failed: {e}"

    def _enter(self, d: Desk, sym: str, px: float, now: datetime) -> None:
        fill = px * (1 + SLIP[sym])
        qty = d.shares_for(fill)
        if qty < 1:
            return
        order = Order(strategy=d.key, symbol=sym, asset_type="equity", side="buy", qty=qty,
                      max_loss=qty * fill * STOP_PCT, cost=qty * fill, mode="paper")
        v = self.risk.check(order, self._acct(d))
        if not v.allowed:
            self.ledger.trade("risk_check", "paper", d.key, sym, "buy", qty, max_loss=order.max_loss,
                              cost=order.cost, note="; ".join(v.reasons))
            log.warning("entry blocked [%s %s]: %s", d.key, sym, v.reasons)
            return
        note = self._paper_order(order)
        d.fill_entry(sym, fill, now)
        self.ledger.trade("entry", "paper", d.key, sym, "buy", qty, price=round(fill, 4), source="yahoo_rt+slip",
                          max_loss=round(order.max_loss, 2), cost=round(order.cost, 2), note=note)
        log.info("ENTRY %s %s x%d @ %.4f (%s)", d.key, sym, qty, fill, note)

    def _exit(self, d: Desk, reason: str, px: float, now: datetime) -> None:
        p = d.pos
        fill = px * (1 - SLIP[p.sym])
        order = Order(strategy=d.key, symbol=p.sym, asset_type="equity", side="sell", qty=p.qty,
                      max_loss=0, cost=0, mode="paper", is_entry=False)
        note = self._paper_order(order)
        tr = d.fill_exit(fill, now, reason)
        self._record(tr)
        self.ledger.trade("exit", "paper", d.key, tr["sym"], "sell", tr["qty"], price=round(fill, 4),
                          source="yahoo_rt+slip", note=f"{reason}; pnl ${tr['pnl_usd']:+.2f}; {note}")
        log.info("EXIT %s %s %s pnl $%.2f (%s)", d.key, tr["sym"], reason, tr["pnl_usd"], note)

    def step(self, now: datetime) -> None:
        """Call once a minute during market hours (now = New York time)."""
        if not self.warmed:
            self.warmup()
        today = now.date().isoformat()
        if self.meta["sod_date"] != today:
            self.meta["sod_date"] = today
            self.meta["sod"] = {k: d.equity() for k, d in self.desks.items()}
        if not self.meta["started"]:
            self.meta["started"] = today
        new: list[tuple] = []
        prices: dict[str, float] = {}
        for s in self.symbols:
            try:
                bars, px = self.md.bars(s, "1d", now=now)
            except Exception as e:  # noqa: BLE001
                log.warning("bars %s failed: %s", s, e)
                continue
            if px:
                prices[s] = px
            latest = bars[-1].t if bars else None
            for b in bars:
                if self.last_t[s] is None or b.t > self.last_t[s]:
                    new.append((b.t, self.order[s], s, b, b.t == latest))
        if "SPY" in prices and not self.meta["benchmark"].get("SPY"):
            self.meta["benchmark"]["SPY"] = {"date": today, "px": prices["SPY"]}
        new.sort(key=lambda e: (e[0], e[1]))
        for _, _, s, b, is_latest in new:
            px = prices.get(s, b.c)
            for d in self.desks.values():                       # exits
                ex = d.exit_check(s, b)
                if ex:
                    self._exit(d, ex[0], px, now)
            self.hub[s].update(b)                               # features
            self.last_t[s] = b.t
            fresh = is_latest and (now - b.t) <= timedelta(minutes=3)
            for d in self.desks.values():                       # entries (fresh bars only)
                if d.wants_entry(s, b, self.hub[s]):
                    if fresh:
                        self._enter(d, s, px, now)
                    else:
                        log.info("skipped stale signal %s %s at %s", d.key, s, b.t)
        if now.time() >= SAFETY_FLAT:                            # never hold overnight
            for d in self.desks.values():
                if d.pos:
                    self._exit(d, "eod_safety", prices.get(d.pos.sym, d.pos.entry_px), now)
        for k, d in self.desks.items():
            self.meta["peak"][k] = max(self.meta["peak"].get(k, d.start_equity), d.equity(prices))
        self.save(prices)

    def status(self) -> list[dict]:
        return [{"desk": k, "label": d.rule.label, "cash": round(d.cash, 2),
                 "position": d.pos.__dict__ if d.pos else None} for k, d in self.desks.items()]
