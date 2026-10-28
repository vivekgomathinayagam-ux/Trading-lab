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
  ledger/daytrade_fills.csv    one row per simulated entry/exit with price provenance (added
                               2026-10-26, Vivek's fixes 1, 2, 4, 5): Yahoo quote time and age,
                               signal-bar time, Skylit cross-check of all six ETFs, and for exits
                               the backtest rule price next to the paper price. Logging only.

Feed fallback (fix 5): if Yahoo fails for a symbol, open positions are valued with Skylit's
spot, and no desk opens a new position until every symbol's Yahoo data is back.
"""
from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path

import yaml

from engine.quotecheck import STALE_QUOTE_S, XCHECK_FLAG_PCT, age_seconds, iso_utc, pct_diff
from engine.risk import AccountState, Order, RiskEngine
from strategies.daytrade.core import (PAPER_RULES, SLIP, STOP_PCT, SYMBOLS, Bar, Desk,
                                      Features)

log = logging.getLogger("daytrade")
CONFIG = Path(__file__).resolve().parent.parent / "strategies" / "daytrade" / "config.yaml"
SAFETY_FLAT = dtime(15, 58)
TRADE_COLS = ["desk", "sym", "qty", "entry_t", "exit_t", "entry_px", "exit_px", "pnl_usd",
              "pnl_pct_equity", "move_pct", "reason", "equity_after"]
FILL_COLS = ["evaluation", "kind", "desk", "sym", "qty", "reason", "bot_time", "signal_bar_start",
             "quote_time", "quote_age_s", "quote_stale", "yahoo_delayed_by_min", "price_source",
             "raw_px", "fill_px", "rule_px", "paper_vs_rule_pct", "skylit_status", "skylit_spot",
             "skylit_as_of", "skylit_diff_pct", "skylit_max_diff_pct", "skylit_flag",
             "skylit_all_diffs", "sandbox"]


def _config() -> dict:
    try:
        return yaml.safe_load(CONFIG.read_text()) or {}
    except Exception:  # noqa: BLE001
        return {}


def enabled() -> bool:
    return _config().get("stage") in ("paper",)


class DayTradeRunner:
    def __init__(self, ledger, broker, risk: RiskEngine, md, ledger_dir: Path,
                 equity: float = 1000.0, symbols=None, rules=None, spot=None):
        self.ledger, self.broker, self.risk, self.md = ledger, broker, risk, md
        self.spot = spot                      # engine.quotecheck.SkylitSpot or None (checks only)
        self.fills_path = ledger_dir / "daytrade_fills.csv"
        self.evaluation = str(_config().get("evaluation", "preliminary"))
        self.price_src: dict[str, str] = {}   # where this step's price per symbol came from
        self.feed: dict = {"yahoo_down": [], "entries_paused": False}
        self._prices: dict[str, float] = {}
        self._xcheck: dict | None = None      # one Skylit call per step, shared by its fills
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
               "evaluation": self.evaluation,
               "feed": {**self.feed, "price_source": dict(self.price_src),
                        "skylit": self.spot.status if self.spot else "unconfigured"},
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

    # ---------------------------------------------------------- provenance (logging only)
    def _cross_check(self) -> dict:
        """Skylit spot for all six ETFs vs this step's prices. One call per step."""
        if self._xcheck is not None:
            return self._xcheck
        res = {"status": "unconfigured", "spots": {}, "diffs": {}}
        if self.spot and self.spot.configured:
            spots = self.spot.spots(self.symbols)
            res["status"] = self.spot.status
            res["spots"] = spots
            for s in self.symbols:
                if self.price_src.get(s) == "skylit_fallback":
                    continue                       # comparing Skylit with itself proves nothing
                d = pct_diff(self._prices.get(s), (spots.get(s) or {}).get("spot"))
                if d is not None:
                    res["diffs"][s] = d
        self._xcheck = res
        return res

    def _log_fill(self, kind: str, d: Desk, sym: str, qty: int, raw_px: float, fill_px: float,
                  reason: str, bar_t: datetime | None, rule_px: float | None, sandbox: str) -> None:
        at = datetime.now(timezone.utc)
        meta = (getattr(self.md, "last_meta", {}) or {}).get(sym, {})
        src = self.price_src.get(sym, "unknown")
        q_epoch = meta.get("quote_epoch") if src == "yahoo_rt" else None
        # quote age = Yahoo's quote time vs when the bot received that price (the price this fill uses)
        age = age_seconds(q_epoch, meta.get("fetched_at") or at)
        x = self._cross_check()
        sk = (x["spots"].get(sym) or {})
        diffs = x["diffs"]
        mx = max((abs(v) for v in diffs.values()), default=None)
        row = {"evaluation": self.evaluation, "kind": kind, "desk": d.key, "sym": sym, "qty": qty,
               "reason": reason, "bot_time": at.isoformat(timespec="seconds"),
               "signal_bar_start": bar_t.isoformat() if bar_t else "",
               "quote_time": iso_utc(q_epoch), "quote_age_s": "" if age is None else age,
               "quote_stale": "" if age is None else (age > STALE_QUOTE_S),
               "yahoo_delayed_by_min": meta.get("delayed_by", "") if src == "yahoo_rt" else "",
               "price_source": src, "raw_px": round(raw_px, 4), "fill_px": round(fill_px, 4),
               "rule_px": "" if rule_px is None else round(rule_px, 4),
               "paper_vs_rule_pct": "" if rule_px is None else pct_diff(raw_px, rule_px),
               "skylit_status": x["status"], "skylit_spot": sk.get("spot", ""),
               "skylit_as_of": sk.get("as_of", ""),
               "skylit_diff_pct": diffs.get(sym, ""),
               "skylit_max_diff_pct": "" if mx is None else mx,
               # Vivek 2026-10-28: flag only the ETF actually traded; the other five stay in
               # skylit_all_diffs / skylit_max_diff_pct for information.
               "skylit_flag": "" if sym not in diffs else (abs(diffs[sym]) > XCHECK_FLAG_PCT),
               "skylit_all_diffs": json.dumps(diffs, separators=(",", ":")) if diffs else "",
               "sandbox": sandbox}
        try:
            new = not self.fills_path.exists()
            with self.fills_path.open("a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FILL_COLS)
                if new:
                    w.writeheader()
                w.writerow(row)
        except OSError as e:                       # logging must never break the desks
            log.error("fills log write failed: %s", e)
        if row["quote_stale"] is True:
            log.warning("STALE QUOTE %s %s %s: %.0fs old", kind, d.key, sym, age)
        if row["skylit_flag"] is True:
            log.warning("PRICE CHECK %s %s: Yahoo vs Skylit diff %.3f%% on the traded ETF (all: %s)",
                        kind, sym, diffs[sym], diffs)

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

    def _enter(self, d: Desk, sym: str, px: float, now: datetime, bar_t: datetime | None = None) -> None:
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
        src = self.price_src.get(sym, "unknown")
        self.ledger.trade("entry", "paper", d.key, sym, "buy", qty, price=round(fill, 4), source=f"{src}+slip",
                          max_loss=round(order.max_loss, 2), cost=round(order.cost, 2), note=note)
        self._log_fill("entry", d, sym, qty, px, fill, "signal", bar_t, None, note)
        log.info("ENTRY %s %s x%d @ %.4f (%s)", d.key, sym, qty, fill, note)

    def _exit(self, d: Desk, reason: str, px: float, now: datetime,
              rule_px: float | None = None, bar_t: datetime | None = None) -> None:
        """rule_px = the price the backtest would use for this exit (stop/target level or the
        15:55 bar's open). Recorded only; the paper fill is unchanged (live price + slippage)."""
        p = d.pos
        fill = px * (1 - SLIP[p.sym])
        order = Order(strategy=d.key, symbol=p.sym, asset_type="equity", side="sell", qty=p.qty,
                      max_loss=0, cost=0, mode="paper", is_entry=False)
        note = self._paper_order(order)
        sym, qty = p.sym, p.qty
        tr = d.fill_exit(fill, now, reason)
        self._record(tr)
        src = self.price_src.get(sym, "unknown")
        self.ledger.trade("exit", "paper", d.key, tr["sym"], "sell", tr["qty"], price=round(fill, 4),
                          source=f"{src}+slip", note=f"{reason}; pnl ${tr['pnl_usd']:+.2f}; {note}")
        self._log_fill("exit", d, sym, qty, px, fill, reason, bar_t, rule_px, note)
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
        self.price_src = {}
        self._xcheck = None
        down: list[str] = []
        for s in self.symbols:
            try:
                bars, px = self.md.bars(s, "1d", now=now)
            except Exception as e:  # noqa: BLE001
                log.warning("bars %s failed: %s", s, e)
                down.append(s)
                continue
            if px:
                prices[s] = px
                self.price_src[s] = "yahoo_rt"
            elif bars:
                self.price_src[s] = "bar_close"      # no live price: falls back to the bar close
            else:
                down.append(s)                      # empty answer counts as a failed feed
            latest = bars[-1].t if bars else None
            for b in bars:
                if self.last_t[s] is None or b.t > self.last_t[s]:
                    new.append((b.t, self.order[s], s, b, b.t == latest))
        # Fix 5: Yahoo failed -> value open positions with Skylit spot; pause all new entries.
        held = {d.pos.sym for d in self.desks.values() if d.pos}
        need = [s for s in down if s in held]
        if need and self.spot and self.spot.configured:
            for s, v in self.spot.spots(need).items():
                if s in need:
                    prices[s] = v["spot"]
                    self.price_src[s] = "skylit_fallback"
        entries_paused = bool(down)
        if down and down != self.feed["yahoo_down"]:
            log.warning("Yahoo feed down for %s: new entries paused; open positions valued with %s",
                        down, "Skylit" if (self.spot and self.spot.configured) else "last known prices")
        if not down and self.feed["yahoo_down"]:
            log.info("Yahoo feed back for all symbols; entries resume on fresh bars")
        self.feed = {"yahoo_down": down, "entries_paused": entries_paused}
        self._prices = prices
        if self.price_src.get("SPY") == "yahoo_rt" and not self.meta["benchmark"].get("SPY"):
            self.meta["benchmark"]["SPY"] = {"date": today, "px": prices["SPY"]}
        new.sort(key=lambda e: (e[0], e[1]))
        for _, _, s, b, is_latest in new:
            if s not in prices:
                self.price_src.setdefault(s, "bar_close")
            px = prices.get(s, b.c)
            for d in self.desks.values():                       # exits
                ex = d.exit_check(s, b)
                if ex:
                    self._exit(d, ex[0], px, now, rule_px=ex[1], bar_t=b.t)
            self.hub[s].update(b)                               # features
            self.last_t[s] = b.t
            fresh = is_latest and (now - b.t) <= timedelta(minutes=3)
            for d in self.desks.values():                       # entries (fresh bars only)
                if d.wants_entry(s, b, self.hub[s]):
                    if entries_paused:
                        log.info("entry skipped (feed down for %s) %s %s at %s", down, d.key, s, b.t)
                    elif fresh:
                        self._enter(d, s, px, now, bar_t=b.t)
                    else:
                        log.info("skipped stale signal %s %s at %s", d.key, s, b.t)
        if now.time() >= SAFETY_FLAT:                            # never hold overnight
            for d in self.desks.values():
                if d.pos:
                    if d.pos.sym not in prices:
                        self.price_src[d.pos.sym] = "entry_px_no_feed"
                    self._exit(d, "eod_safety", prices.get(d.pos.sym, d.pos.entry_px), now)
        for k, d in self.desks.items():
            self.meta["peak"][k] = max(self.meta["peak"].get(k, d.start_equity), d.equity(prices))
        self.save(prices)

    def status(self) -> list[dict]:
        return [{"desk": k, "label": d.rule.label, "cash": round(d.cash, 2),
                 "position": d.pos.__dict__ if d.pos else None} for k, d in self.desks.items()]
