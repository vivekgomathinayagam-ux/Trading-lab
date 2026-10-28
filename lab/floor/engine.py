"""Replay historical bars through the shared day-trade desks (strategies/daytrade/core.py).

The loop is the same order of operations the live bot uses:
  1. pending entry fills at this bar's open (+ slippage)
  2. exits (stop / target / 15:55 flat) against this bar's range (- slippage)
  3. features update with this bar
  4. entry signals at this bar's close -> pending for the next bar of that symbol
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from strategies.daytrade.core import SIGNAL_EXITS, SLIP, SYMBOLS, Bar, Desk, Features, Rule


def simulate(bars: dict[str, list[Bar]], rules: Iterable[Rule], bar_minutes: int = 1,
             equity: float = 1000.0, slip_mult: float = 1.0, warmup_days: int = 3,
             trade_from_day=None) -> dict:
    """trade_from_day (a date) overrides warmup_days: trade only from that day on (parity replay)."""
    syms = [s for s in SYMBOLS if bars.get(s)]
    order = {s: i for i, s in enumerate(SYMBOLS)}
    hub = {s: Features(bar_minutes=bar_minutes) for s in syms}
    desks = [Desk(rule=r, cash=equity, start_equity=equity) for r in rules]
    events = sorted(((b.t, order[s], s, b) for s in syms for b in bars[s]), key=lambda e: (e[0], e[1]))
    days = sorted({b.t.date() for s in syms for b in bars[s]})
    trade_from = days[warmup_days] if len(days) > warmup_days else None
    if trade_from_day is not None:
        trade_from = trade_from_day
    eod_equity = {d.key: {} for d in desks}
    marks: dict[str, float] = {}
    first_px: dict[str, float] = {}
    last_px: dict[str, float] = {}
    pending_exit: dict[str, tuple[str, str]] = {}          # desk key -> (sym, reason): signal exits fill next bar open
    for t, _, sym, bar in events:
        slip = SLIP[sym] * slip_mult
        trading = trade_from is not None and bar.t.date() >= trade_from
        for d in desks:                                   # 0. pending signal exits
            pe = pending_exit.get(d.key)
            if pe and pe[0] == sym and d.pos and d.pos.sym == sym:
                d.fill_exit(bar.o * (1 - slip), bar.t, pe[1])
                del pending_exit[d.key]
        for d in desks:                                   # 1. pending fills
            if d.pending == sym:
                if d.pending_valid(bar):
                    d.fill_entry(sym, bar.o * (1 + slip), bar.t)
                else:
                    d.pending = d.pending_day = None
        for d in desks:                                   # 2. exits
            ex = d.exit_check(sym, bar)
            if ex and ex[0] in SIGNAL_EXITS:
                pending_exit[d.key] = (sym, ex[0])
            elif ex:
                pending_exit.pop(d.key, None)
                d.fill_exit(ex[1] * (1 - slip), bar.t, ex[0])
        hub[sym].update(bar)                              # 3. features
        if trading:                                       # 4. signals
            for d in desks:
                if d.wants_entry(sym, bar, hub[sym]):
                    d.pending, d.pending_day = sym, bar.t.date().isoformat()
            first_px.setdefault(sym, bar.o)
        marks[sym] = bar.c
        last_px[sym] = bar.c
        if trading:
            for d in desks:
                eod_equity[d.key][bar.t.date().isoformat()] = d.equity(marks)
    for d in desks:                                       # anything still open (data ended mid-day)
        if d.pos:
            d.fill_exit(last_px[d.pos.sym] * (1 - SLIP[d.pos.sym] * slip_mult), events[-1][0], "end")
            eod_equity[d.key][events[-1][0].date().isoformat()] = d.cash
    bench = {s: round((last_px[s] / first_px[s] - 1) * 100, 2) for s in first_px}
    return {"desks": desks, "eod_equity": eod_equity, "benchmark_pct": bench,
            "sessions": len([d for d in days if trade_from and d >= trade_from]),
            "first_day": str(trade_from) if trade_from else None, "last_day": str(days[-1]) if days else None}


def desk_metrics(desk: Desk, eod: dict[str, float]) -> dict:
    tr = desk.trades
    pnl = [t["pnl_pct_equity"] for t in tr]
    wins = [p for p in pnl if p > 0]
    losses = [p for p in pnl if p <= 0]
    pf = (sum(wins) / -sum(losses)) if losses and sum(losses) < 0 else (99.0 if wins else 0.0)
    curve = [v for _, v in sorted(eod.items())]
    peak, mdd = -1e18, 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)
    rets = [curve[i] / curve[i - 1] - 1 for i in range(1, len(curve))]
    mean = sum(rets) / len(rets) if rets else 0.0
    sd = (sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 if len(rets) > 1 else 0.0
    by_reason = defaultdict(int)
    by_sym = defaultdict(lambda: [0, 0.0])
    for t in tr:
        by_reason[t["reason"]] += 1
        by_sym[t["sym"]][0] += 1
        by_sym[t["sym"]][1] += t["pnl_usd"]
    end_eq = curve[-1] if curve else desk.start_equity
    return {
        "desk": desk.key, "label": desk.rule.label, "trades": len(tr),
        "win_rate_pct": round(len(wins) / len(pnl) * 100, 1) if pnl else 0.0,
        "avg_win_pct": round(sum(wins) / len(wins), 2) if wins else 0.0,
        "avg_loss_pct": round(sum(losses) / len(losses), 2) if losses else 0.0,
        "expectancy_pct": round(sum(pnl) / len(pnl), 3) if pnl else 0.0,
        "profit_factor": round(pf, 2),
        "total_return_pct": round((end_eq / desk.start_equity - 1) * 100, 2),
        "end_equity": round(end_eq, 2),
        "max_dd_pct": round(mdd * 100, 2),
        "sharpe_daily_ann": round(mean / sd * 252 ** 0.5, 2) if sd > 0 else 0.0,
        "exits": dict(by_reason),
        "by_symbol": {s: {"trades": n, "pnl_usd": round(p, 2)} for s, (n, p) in sorted(by_sym.items())},
        "targets_hit": by_reason.get("target", 0),
    }
