"""Pre-registered BTC/ETH strategies for the Crypto Pier.

Every signal at bar i uses data up to and including bar i only. Rolling
"prior N bars" levels are shifted by one so the current bar never sees itself.
Higher-timeframe filters on intraday bars use the PREVIOUS completed day.

Main parameters were fixed before any run, from common published defaults,
not tuned. VARIANTS adds a small sensitivity grid that is reported, never used
to pick the headline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from .engine import Signals


# ---------------------------------------------------------------- indicators

def sma(x: pd.Series, n: int) -> pd.Series:
    return x.rolling(n, min_periods=n).mean()


def ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=n, adjust=False, min_periods=n).mean()


def atr(df: pd.DataFrame, n: int) -> pd.Series:
    prev = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()],
                   axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean()


def rsi(x: pd.Series, n: int) -> pd.Series:
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100.0)


def prior_day_filter(intraday: pd.DataFrame, daily_df: pd.DataFrame, n: int) -> pd.Series:
    """True when the previous completed day's close is above its n-day SMA."""
    ok = (daily_df["close"] > sma(daily_df["close"], n)).shift(1)  # yesterday's verdict
    day = intraday.index.floor("1D")
    return pd.Series(ok.reindex(day).to_numpy(), index=intraday.index).fillna(False).astype(bool)


def _arr(s: pd.Series, fill=False) -> np.ndarray:
    return s.fillna(fill).to_numpy()


def _sig(enter, exit_, stop_dist, target=None, trail=False, max_hold=None) -> Signals:
    n = len(enter)
    tgt = np.ones(n) if target is None else _arr(target, 0.0).astype(float)
    return Signals(_arr(enter).astype(bool), _arr(exit_).astype(bool),
                   stop_dist.to_numpy(float), tgt, trail, max_hold)


# ---------------------------------------------------------------- strategies
# Each builder: (bars, daily_bars, **params) -> Signals

def buy_hold(df, daily_df):
    n = len(df)
    enter = np.zeros(n, bool)
    enter[0] = True  # decided at first close, fills at second open
    return Signals(enter, np.zeros(n, bool), np.full(n, np.nan), np.ones(n))


def trend_sma(df, daily_df, n=100, atr_n=20, k=3.0):
    """Swing/position. Long while close > SMA(n); trailing k*ATR stop."""
    m = sma(df["close"], n)
    return _sig(df["close"] > m, df["close"] < m, k * atr(df, atr_n), trail=True)


def trend_voltarget(df, daily_df, n=100, vol=0.40, atr_n=20, k=3.0):
    """Trend_sma, but exposure = target vol / realized 30-day vol (max 1)."""
    m = sma(df["close"], n)
    rv = df["close"].pct_change().rolling(30, min_periods=30).std() * np.sqrt(365)
    tgt = (vol / rv).clip(upper=1.0)
    return _sig(df["close"] > m, df["close"] < m, k * atr(df, atr_n), target=tgt, trail=True)


def donchian(df, daily_df, entry_n=20, exit_n=10, atr_n=20, k=2.0):
    """Turtle-style breakout: buy a close above the prior entry_n-bar high,
    sell a close below the prior exit_n-bar low; fixed k*ATR initial stop."""
    hi = df["high"].rolling(entry_n, min_periods=entry_n).max().shift(1)
    lo = df["low"].rolling(exit_n, min_periods=exit_n).min().shift(1)
    return _sig(df["close"] > hi, df["close"] < lo, k * atr(df, atr_n))


def rsi2_meanrev(df, daily_df, rsi_n=2, buy_below=10, trend_n=200, exit_n=5, hold=10, atr_n=20, k=3.0):
    """Buy short-term dips inside an uptrend; exit on a bounce or after `hold` bars."""
    r = rsi(df["close"], rsi_n)
    up = df["close"] > sma(df["close"], trend_n)
    return _sig((r < buy_below) & up, df["close"] > sma(df["close"], exit_n), k * atr(df, atr_n),
                max_hold=hold)


def ema_cross(df, daily_df, fast=20, slow=50, atr_n=20, k=3.0):
    """Swing on 4h bars: long while EMA(fast) > EMA(slow); trailing stop."""
    f, s = ema(df["close"], fast), ema(df["close"], slow)
    return _sig(f > s, f < s, k * atr(df, atr_n), trail=True)


def intraday_breakout(df, daily_df, look=24, hold=12, trend_n=50, atr_n=24, k=1.5):
    """Day trade on 1h bars: buy a close above the prior `look`-hour high when
    yesterday closed above its trend_n-day SMA; out after `hold` hours or stop."""
    hi = df["high"].rolling(look, min_periods=look).max().shift(1)
    ok = prior_day_filter(df, daily_df, trend_n)
    never = pd.Series(False, index=df.index)
    return _sig((df["close"] > hi) & ok, never, k * atr(df, atr_n), trail=True, max_hold=hold)


def intraday_meanrev(df, daily_df, rsi_n=14, buy_below=25, exit_above=50, hold=24, trend_n=50,
                     atr_n=24, k=2.0):
    """Day trade on 1h bars: buy oversold hourly RSI inside a daily uptrend."""
    r = rsi(df["close"], rsi_n)
    ok = prior_day_filter(df, daily_df, trend_n)
    return _sig((r < buy_below) & ok, r > exit_above, k * atr(df, atr_n), max_hold=hold)


# --------------------------------------------------- short-horizon patterns
# Fixed, short holding periods (days), meant to be tradeable via a short-dated
# long call/put on a crypto ETF (defined risk = premium paid) instead of the
# spot position the backtest actually simulates. A stop here is a simulated
# close-out, not an options Greek; it does not model theta, IV or the ETF's
# tracking error against spot, which real paper trading would need to check.

def extreme_drop_bounce(df, daily_df, drop_pct=10.0, hold=5, atr_n=14, k=1.5):
    """Mean reversion: buy after a single-day drop of drop_pct% or more,
    hold up to `hold` days, fixed stop at k*ATR (a put would be the mirror)."""
    ret1 = df["close"].pct_change()
    enter = ret1 < -drop_pct / 100.0
    never = pd.Series(False, index=df.index)
    return _sig(enter, never, k * atr(df, atr_n), max_hold=hold)


def momentum_burst(df, daily_df, lookback=3, thresh_pct=15.0, hold=5, atr_n=14, k=2.0):
    """Continuation: buy after a thresh_pct% move over the last `lookback`
    days, hold up to `hold` days, fixed stop at k*ATR."""
    mom = df["close"].pct_change(lookback)
    enter = mom > thresh_pct / 100.0
    never = pd.Series(False, index=df.index)
    return _sig(enter, never, k * atr(df, atr_n), max_hold=hold)


def squeeze_breakout(df, daily_df, squeeze_n=20, breakout_n=10, atr_n=14, k=1.5, hold=10):
    """Volatility-contraction breakout: when ATR% is in its lowest quartile
    of the last squeeze_n days, buy a close above the prior breakout_n-day
    high; trailing k*ATR stop, time exit after `hold` days."""
    atr_pct = atr(df, atr_n) / df["close"]
    squeezed = atr_pct <= atr_pct.rolling(squeeze_n, min_periods=squeeze_n).quantile(0.25)
    hi = df["high"].rolling(breakout_n, min_periods=breakout_n).max().shift(1)
    enter = (df["close"] > hi) & squeezed
    never = pd.Series(False, index=df.index)
    return _sig(enter, never, k * atr(df, atr_n), trail=True, max_hold=hold)


@dataclass(frozen=True)
class Spec:
    key: str
    style: str        # swing | day | control
    timeframe: str    # 1d | 4h | 1h
    builder: Callable
    params: dict = field(default_factory=dict)
    main: bool = True

    @property
    def name(self) -> str:
        if not self.params:
            return self.key
        return self.key + "(" + ",".join(f"{k}={v}" for k, v in self.params.items()) + ")"


MAIN = [
    Spec("trend_sma", "swing", "1d", trend_sma, {"n": 100}),
    Spec("trend_voltarget", "swing", "1d", trend_voltarget, {"n": 100, "vol": 0.40}),
    Spec("donchian", "swing", "1d", donchian, {"entry_n": 20, "exit_n": 10}),
    Spec("rsi2_meanrev", "swing", "1d", rsi2_meanrev, {"buy_below": 10, "trend_n": 200}),
    Spec("ema_cross_4h", "swing", "4h", ema_cross, {"fast": 20, "slow": 50}),
    Spec("intraday_breakout", "day", "1h", intraday_breakout, {"look": 24, "hold": 12}),
    Spec("intraday_meanrev", "day", "1h", intraday_meanrev, {"buy_below": 25}),
]

VARIANTS = [
    Spec("trend_sma", "swing", "1d", trend_sma, {"n": 50}, False),
    Spec("trend_sma", "swing", "1d", trend_sma, {"n": 150}, False),
    Spec("trend_sma", "swing", "1d", trend_sma, {"n": 200}, False),
    Spec("trend_voltarget", "swing", "1d", trend_voltarget, {"n": 100, "vol": 0.30}, False),
    Spec("trend_voltarget", "swing", "1d", trend_voltarget, {"n": 100, "vol": 0.60}, False),
    Spec("donchian", "swing", "1d", donchian, {"entry_n": 55, "exit_n": 20}, False),
    Spec("donchian", "swing", "1d", donchian, {"entry_n": 10, "exit_n": 5}, False),
    Spec("rsi2_meanrev", "swing", "1d", rsi2_meanrev, {"buy_below": 5, "trend_n": 200}, False),
    Spec("rsi2_meanrev", "swing", "1d", rsi2_meanrev, {"buy_below": 15, "trend_n": 100}, False),
    Spec("ema_cross_4h", "swing", "4h", ema_cross, {"fast": 10, "slow": 30}, False),
    Spec("ema_cross_4h", "swing", "4h", ema_cross, {"fast": 50, "slow": 200}, False),
    Spec("intraday_breakout", "day", "1h", intraday_breakout, {"look": 12, "hold": 6}, False),
    Spec("intraday_breakout", "day", "1h", intraday_breakout, {"look": 48, "hold": 24}, False),
    Spec("intraday_meanrev", "day", "1h", intraday_meanrev, {"buy_below": 20}, False),
    Spec("intraday_meanrev", "day", "1h", intraday_meanrev, {"buy_below": 30}, False),
]

PATTERNS_MAIN = [
    Spec("drop_bounce", "pattern", "1d", extreme_drop_bounce, {"drop_pct": 10.0, "hold": 5}),
    Spec("momentum_burst", "pattern", "1d", momentum_burst, {"lookback": 3, "thresh_pct": 15.0, "hold": 5}),
    Spec("squeeze_breakout", "pattern", "1d", squeeze_breakout, {"squeeze_n": 20, "breakout_n": 10, "hold": 10}),
]

PATTERNS_VARIANTS = [
    Spec("drop_bounce", "pattern", "1d", extreme_drop_bounce, {"drop_pct": 7.0, "hold": 3}, False),
    Spec("drop_bounce", "pattern", "1d", extreme_drop_bounce, {"drop_pct": 15.0, "hold": 7}, False),
    Spec("momentum_burst", "pattern", "1d", momentum_burst, {"lookback": 5, "thresh_pct": 20.0, "hold": 7}, False),
    Spec("momentum_burst", "pattern", "1d", momentum_burst, {"lookback": 2, "thresh_pct": 10.0, "hold": 3}, False),
    Spec("squeeze_breakout", "pattern", "1d", squeeze_breakout, {"squeeze_n": 30, "breakout_n": 20, "hold": 15}, False),
]

CONTROL = Spec("buy_hold", "control", "1d", buy_hold, {})
