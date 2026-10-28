"""Day-trade desks: one source of truth for the backtest lab AND the live paper bot.

lab/floor runs these classes over historical 1-minute bars; the Railway bot runs
them over live 1-minute bars. Pure Python (the bot has no pandas). The rules are
pre-registered in strategies/daytrade/spec.md; read that before changing anything.

Per bar, in this order (both lab and bot):
  1. a pending entry fills at this bar's open (lab) / at the live price (bot)
  2. exits: stop / target / 15:55 flat, checked against this bar's range
  3. features update with this bar (bar close)
  4. entry signal decided at this bar's close -> pending for the next bar
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from datetime import date, datetime, time as dtime
from statistics import median
from typing import Optional

SYMBOLS = ["SPY", "QQQ", "TQQQ", "UPRO", "SQQQ", "SPXU"]  # priority order on ties
LEVERAGED = {"TQQQ", "UPRO", "SQQQ", "SPXU"}
SLIP = {s: (0.0005 if s in LEVERAGED else 0.0002) for s in SYMBOLS}  # per side, fraction

TARGET_PCT = 0.05
STOP_PCT = 0.025
OPEN_MIN = 9 * 60 + 30            # 09:30 ET in minutes
ENTRY_START = dtime(9, 35)
ENTRY_END = dtime(15, 30)
FLAT_AT = dtime(15, 55)
VOL_MULT = 3.0
MINUTE_MULT = 1.5


@dataclass(frozen=True)
class Bar:
    t: datetime   # bar OPEN time, timezone-aware America/New_York
    o: float
    h: float
    l: float
    c: float
    v: float


# ------------------------------------------------------------------ features
class Features:
    """Rolling per-symbol state. Everything is computed from the current bar and
    earlier bars only (no look-ahead)."""

    def __init__(self, bar_minutes: int = 1, vol_lookback: int = 20, same_minute_days: int = 5,
                 breakout_lookback: int = 15, or_minutes: int = 15, ema_fast: int = 9,
                 ema_slow: int = 21, ema_bucket_minutes: int = 5):
        self.bm = bar_minutes
        self.or_minutes = or_minutes
        self.ema_bucket = ema_bucket_minutes
        self.kf, self.ks = 2 / (ema_fast + 1), 2 / (ema_slow + 1)
        self.ema_slow_n = ema_slow
        self.same_minute_days = same_minute_days
        self.vols: deque = deque(maxlen=vol_lookback)
        self.minute_hist: dict[int, deque] = {}
        self.today_minute_vols: dict[int, float] = {}
        self.highs: deque = deque(maxlen=max(1, breakout_lookback // bar_minutes))
        self.day: Optional[date] = None
        self.pv = self.vv = 0.0
        self.or_high: Optional[float] = None
        self.or_low: Optional[float] = None
        self.ema_f: Optional[float] = None
        self.ema_s: Optional[float] = None
        self.ema_n = 0
        self.prev_diff: Optional[float] = None
        self.bucket: list[tuple[float, float]] = []   # (vol_ratio, minute_ratio) of bars in the open bucket
        self.last_bucket: list[tuple[float, float]] = []
        self.prev_close: Optional[float] = None
        self._prev_close_today: Optional[float] = None
        # values for the latest bar
        self.vol_ratio = math.nan
        self.minute_ratio = math.nan
        self.vwap = math.nan
        self.prior_high = math.nan
        self.cross_up = False
        self.minute = 0
        # ema_vol_v2: clock-based 5-minute buckets (additive; v1 fields above are untouched)
        self.ema2_f: Optional[float] = None
        self.ema2_s: Optional[float] = None
        self.ema2_n = 0
        self.prev_diff2: Optional[float] = None
        self.bucket2: list[tuple[float, float]] = []
        self.bucket2_id: Optional[int] = None
        self.bucket2_close: Optional[float] = None
        self.cross_up_v2 = False
        self.cross_bucket2: list[tuple[float, float]] = []

    def _new_day(self, d: date) -> None:
        for m, v in self.today_minute_vols.items():
            self.minute_hist.setdefault(m, deque(maxlen=self.same_minute_days)).append(v)
        self.today_minute_vols = {}
        self.highs.clear()
        self.pv = self.vv = 0.0
        self.or_high = self.or_low = None
        self.bucket = []
        self.bucket2 = []
        self.bucket2_id = None
        self.day = d

    def update(self, bar: Bar) -> None:
        d = bar.t.date()
        if d != self.day:
            self._new_day(d)
        m = bar.t.hour * 60 + bar.t.minute - OPEN_MIN
        self.minute = m
        prev_close = self.prev_close if self.highs else None   # today's previous close only
        # ratios against PRIOR bars only
        prior = list(self.vols)
        med = median(prior) if len(prior) >= 10 else 0.0
        self.vol_ratio = bar.v / med if med > 0 else math.nan
        hist = self.minute_hist.get(m)
        if hist and len(hist) >= 3 and sum(hist) > 0:
            self.minute_ratio = bar.v / (sum(hist) / len(hist))
        else:
            self.minute_ratio = math.nan
        self.prior_high = max(self.highs) if len(self.highs) == self.highs.maxlen else math.nan
        self._prev_close_today = prev_close
        # add this bar
        self.vols.append(bar.v)
        self.today_minute_vols[m] = bar.v
        self.highs.append(bar.h)
        tp = (bar.h + bar.l + bar.c) / 3
        self.pv += tp * bar.v
        self.vv += bar.v
        self.vwap = self.pv / self.vv if self.vv > 0 else bar.c
        if m < self.or_minutes:
            self.or_high = bar.h if self.or_high is None else max(self.or_high, bar.h)
            self.or_low = bar.l if self.or_low is None else min(self.or_low, bar.l)
        # 5-minute EMA buckets (a bucket closes when this bar ends on a 5-minute boundary)
        self.bucket.append((self.vol_ratio, self.minute_ratio))
        self.cross_up = False
        if (m + self.bm) % self.ema_bucket == 0:
            c = bar.c
            if self.ema_f is None:
                self.ema_f = self.ema_s = c
            else:
                self.ema_f = c * self.kf + self.ema_f * (1 - self.kf)
                self.ema_s = c * self.ks + self.ema_s * (1 - self.ks)
            self.ema_n += 1
            diff = self.ema_f - self.ema_s
            self.cross_up = (self.prev_diff is not None and self.prev_diff <= 0 < diff
                             and self.ema_n > self.ema_slow_n)
            self.prev_diff = diff
            self.last_bucket, self.bucket = self.bucket, []
        self._update_v2(m, bar)
        self.prev_close = bar.c

    def _close_bucket2(self, c: float) -> bool:
        if self.ema2_f is None:
            self.ema2_f = self.ema2_s = c
        else:
            self.ema2_f = c * self.kf + self.ema2_f * (1 - self.kf)
            self.ema2_s = c * self.ks + self.ema2_s * (1 - self.ks)
        self.ema2_n += 1
        diff = self.ema2_f - self.ema2_s
        crossed = (self.prev_diff2 is not None and self.prev_diff2 <= 0 < diff and self.ema2_n > self.ema_slow_n)
        self.prev_diff2 = diff
        done, self.bucket2 = self.bucket2, []
        if crossed:
            self.cross_bucket2 = done
        return crossed

    def _update_v2(self, m: int, bar: Bar) -> None:
        """5-minute buckets by clock: a bucket closes on its last minute's bar, or, if that bar is
        missing, when the first bar of a later bucket arrives (that bar then starts the new bucket)."""
        self.cross_up_v2 = False
        bid = m // self.ema_bucket
        if self.bucket2_id is not None and bid != self.bucket2_id and self.bucket2:
            self.cross_up_v2 |= self._close_bucket2(self.bucket2_close)
        self.bucket2.append((self.vol_ratio, self.minute_ratio))
        self.bucket2_id = bid
        self.bucket2_close = bar.c
        if (m + self.bm) % self.ema_bucket == 0:
            self.cross_up_v2 |= self._close_bucket2(bar.c)

    # --- volume tests on the latest bar
    @staticmethod
    def _spike(vol_ratio: float, minute_ratio: float, mult: float) -> bool:
        if not (vol_ratio >= mult):          # nan -> False
            return False
        if math.isnan(minute_ratio):         # fewer than 3 sessions of history
            return True
        return minute_ratio >= MINUTE_MULT

    def volume_ok(self, mult: float = VOL_MULT) -> bool:
        return self._spike(self.vol_ratio, self.minute_ratio, mult)

    def bucket_volume_ok(self, mult: float = VOL_MULT) -> bool:
        return any(self._spike(v, mr, mult) for v, mr in self.last_bucket)

    def cross_bucket2_volume_ok(self, mult: float = VOL_MULT) -> bool:
        return any(self._spike(v, mr, mult) for v, mr in self.cross_bucket2)

    @property
    def or_done(self) -> bool:
        return self.minute >= self.or_minutes and self.or_high is not None


# ------------------------------------------------------------------ rules
class Rule:
    key = "rule"
    label = "Rule"

    def signal(self, f: Features, bar: Bar) -> bool:
        raise NotImplementedError

    # Optional hooks (added 2026-10-28). The base versions do nothing, so the original desks are
    # unchanged. Desk.exit_check calls observe() once for every bar of every symbol, BEFORE the
    # shared feature update; a rule may keep its own state there and return an exit reason, decided
    # at this bar's close, for the symbol the desk holds.
    def observe(self, sym: str, bar: Bar) -> Optional[str]:
        return None

    def reset(self) -> None:
        return None


class ORB(Rule):
    """Close crosses above the 09:30-09:45 range high (optionally on a volume spike)."""

    def __init__(self, vol_mult: Optional[float] = VOL_MULT):
        self.vol = vol_mult
        self.key = "orb_vol" if vol_mult else "orb_plain"
        self.label = "ORB + volume" if vol_mult else "ORB (no volume filter)"

    def signal(self, f: Features, bar: Bar) -> bool:
        if not f.or_done:
            return False
        prev = f._prev_close_today
        crossed = bar.c > f.or_high and (prev is None or prev <= f.or_high)
        return crossed and (self.vol is None or f.volume_ok(self.vol))


class EMACross(Rule):
    """5-minute EMA 9 crosses above EMA 21 (optionally with a 1-minute volume spike in that bucket)."""

    def __init__(self, vol_mult: Optional[float] = VOL_MULT):
        self.vol = vol_mult
        self.key = "ema_vol" if vol_mult else "ema_plain"
        self.label = "EMA 9/21 + volume" if vol_mult else "EMA 9/21 (no volume filter)"

    def signal(self, f: Features, bar: Bar) -> bool:
        if not f.cross_up or bar.t.time() < dtime(9, 45):
            return False
        return self.vol is None or f.bucket_volume_ok(self.vol)


class VolSpike(Rule):
    """Volume spike bar that closes up, above VWAP and above the prior 15-bar high."""

    def __init__(self, vol_mult: float = VOL_MULT):
        self.vol = vol_mult
        self.key = "volspike" if vol_mult == VOL_MULT else f"volspike_{vol_mult:g}x"
        self.label = "Volume spike" if vol_mult == VOL_MULT else f"Volume spike ({vol_mult:g}x)"

    def signal(self, f: Features, bar: Bar) -> bool:
        return (f.volume_ok(self.vol) and bar.c > bar.o and bar.c > f.vwap
                and not math.isnan(f.prior_high) and bar.c > f.prior_high)


class EMACrossV2(Rule):
    """ema_vol_v2: EMACross with clock-based 5-minute buckets (spec addendum 2026-10-28)."""
    key = "ema_vol_v2"
    label = "EMA 9/21 + volume v2"

    def __init__(self, vol_mult: float = VOL_MULT):
        self.vol = vol_mult

    def signal(self, f: Features, bar: Bar) -> bool:
        if not f.cross_up_v2 or bar.t.time() < dtime(9, 45):
            return False
        return f.cross_bucket2_volume_ok(self.vol)


class _CVD3:
    """Session CVD on 3-minute clock candles, delta approximated by close-location value
    (strategies/cvd_turn/spec.md). update() returns 'buy' / 'sell' / None at a candle close."""
    CANDLE = 3
    LOOK = 5
    SPIKE_MULT = 3.0

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.day: Optional[date] = None
        self.cvd: list[float] = []
        self.ranges: list[float] = []
        self.cur_id: Optional[int] = None
        self.cur: Optional[list] = None      # [delta, high, low]
        self.spike = False

    def _close(self) -> Optional[str]:
        delta, h, l = self.cur
        self.cur = None
        self.cvd.append((self.cvd[-1] if self.cvd else 0.0) + delta)
        rng = h - l
        prior = self.ranges[:]
        self.ranges.append(rng)
        k = len(self.cvd) - 1
        self.spike = len(prior) >= self.LOOK and rng > self.SPIKE_MULT * median(prior)
        if k < self.LOOK:
            return None
        win = self.cvd[k - self.LOOK:k]
        if self.cvd[k - 1] == min(win) and self.cvd[k] > self.cvd[k - 1]:
            return "buy"
        if self.cvd[k - 1] == max(win) and self.cvd[k] < self.cvd[k - 1]:
            return "sell"
        return None

    def update(self, bar: Bar) -> Optional[str]:
        d = bar.t.date()
        if d != self.day:
            self.reset()
            self.day = d
        m = bar.t.hour * 60 + bar.t.minute - OPEN_MIN
        if m < 0:
            return None
        cid = m // self.CANDLE
        ev, spike = None, False
        if self.cur is not None and cid != self.cur_id:
            ev = self._close()                       # last bar of that candle was missing
            spike = self.spike
        rng = bar.h - bar.l
        delta = bar.v * ((bar.c - bar.l) - (bar.h - bar.c)) / rng if rng > 0 else 0.0
        if self.cur is None:
            self.cur = [0.0, bar.h, bar.l]
        self.cur[0] += delta
        self.cur[1] = max(self.cur[1], bar.h)
        self.cur[2] = min(self.cur[2], bar.l)
        self.cur_id = cid
        if (m + 1) % self.CANDLE == 0:
            ev2 = self._close()
            if ev2 or ev is None:
                ev, spike = ev2, self.spike
        self.spike = spike                           # spike flag of the candle behind `ev`
        return ev


class CVDTurn(Rule):
    """CVD turn on 3-minute candles (strategies/cvd_turn/spec.md). Trades one symbol on its own
    CVD: buy turn -> entry (skipped on a fast-spike candle); sell turn -> exit."""

    def __init__(self, sym: str):
        self.sym = sym
        self.key = f"cvd_{sym.lower()}"
        self.label = f"CVD turn 3-min ({sym})"
        self.cvd = _CVD3()
        self.last: tuple = (None, None, False)     # (bar time, event, spike)

    def reset(self) -> None:
        self.cvd.reset()
        self.last = (None, None, False)

    def observe(self, sym: str, bar: Bar) -> Optional[str]:
        if sym != self.sym:
            return None
        ev = self.cvd.update(bar)
        self.last = (bar.t, ev, self.cvd.spike)
        return "cvd_sell" if ev == "sell" else None

    def signal(self, f: Features, bar: Bar) -> bool:
        t, ev, spike = self.last
        return t == bar.t and ev == "buy" and not spike


SIGNAL_EXITS = {"cvd_sell"}

PAPER_RULES = [ORB(), EMACross(), VolSpike(),
               # added by the Researcher 2026-10-28 (pre-registered: strategies/cvd_turn/spec.md, daytrade spec addendum)
               EMACrossV2(), CVDTurn("SPY"), CVDTurn("TQQQ")]
COMPARISON_RULES = [ORB(None), EMACross(None), VolSpike(2.0)]


# ------------------------------------------------------------------ desk
@dataclass
class Position:
    sym: str
    qty: int
    entry_px: float
    stop: float
    target: float
    entry_t: str


@dataclass
class Desk:
    """One $-book per rule, one position at a time, one entry per day."""
    rule: Rule
    cash: float = 1000.0
    start_equity: float = 1000.0
    target_pct: float = TARGET_PCT
    stop_pct: float = STOP_PCT
    pos: Optional[Position] = None
    pending: Optional[str] = None
    pending_day: Optional[str] = None
    last_entry_day: Optional[str] = None
    trades: list = field(default_factory=list)

    def __post_init__(self):
        self.rule.reset()

    @property
    def key(self) -> str:
        return self.rule.key

    def equity(self, marks: Optional[dict] = None) -> float:
        if not self.pos:
            return self.cash
        px = (marks or {}).get(self.pos.sym, self.pos.entry_px)
        return self.cash + self.pos.qty * px

    # step 2: exits
    def exit_check(self, sym: str, bar: Bar) -> Optional[tuple[str, float]]:
        sig = self.rule.observe(sym, bar)        # base Rule: always None (original desks unchanged)
        p = self.pos
        if not p or p.sym != sym:
            return None
        if bar.t.time() >= FLAT_AT:
            return ("eod", bar.o)
        if bar.l <= p.stop:
            return ("stop", min(bar.o, p.stop))
        if bar.h >= p.target:
            return ("target", max(bar.o, p.target))
        if sig:
            return (sig, bar.c)                  # decided at this bar's close; lab fills next open
        return None

    # step 4: entries
    def wants_entry(self, sym: str, bar: Bar, f: Features) -> bool:
        if self.pos or self.pending:
            return False
        if self.last_entry_day == bar.t.date().isoformat():
            return False
        if not (ENTRY_START <= bar.t.time() < ENTRY_END):
            return False
        return self.rule.signal(f, bar)

    def pending_valid(self, bar: Bar) -> bool:
        return (self.pending_day == bar.t.date().isoformat() and bar.t.time() < ENTRY_END)

    def shares_for(self, px: float) -> int:
        return int(self.cash // px) if px > 0 else 0

    def fill_entry(self, sym: str, px: float, t: datetime) -> Optional[Position]:
        self.pending = self.pending_day = None
        qty = self.shares_for(px)
        if qty < 1:
            return None
        self.cash -= qty * px
        self.pos = Position(sym, qty, px, px * (1 - self.stop_pct), px * (1 + self.target_pct), t.isoformat())
        self.last_entry_day = t.date().isoformat()
        return self.pos

    def fill_exit(self, px: float, t: datetime, reason: str) -> dict:
        p = self.pos
        assert p is not None
        eq_before = self.cash + p.qty * p.entry_px
        self.cash += p.qty * px
        pnl = p.qty * (px - p.entry_px)
        tr = {"desk": self.key, "sym": p.sym, "qty": p.qty, "entry_t": p.entry_t, "exit_t": t.isoformat(),
              "entry_px": round(p.entry_px, 4), "exit_px": round(px, 4), "pnl_usd": round(pnl, 2),
              "pnl_pct_equity": round(pnl / eq_before * 100, 3),
              "move_pct": round((px / p.entry_px - 1) * 100, 3), "reason": reason,
              "equity_after": round(self.cash, 2)}
        self.trades.append(tr)
        self.pos = None
        return tr

    # persistence (bot)
    def to_dict(self) -> dict:
        return {"cash": self.cash, "start_equity": self.start_equity, "last_entry_day": self.last_entry_day,
                "pos": self.pos.__dict__ if self.pos else None}

    def load(self, d: dict) -> None:
        self.cash = float(d.get("cash", self.cash))
        self.start_equity = float(d.get("start_equity", self.start_equity))
        self.last_entry_day = d.get("last_entry_day")
        self.pos = Position(**d["pos"]) if d.get("pos") else None
