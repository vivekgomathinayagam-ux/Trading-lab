"""Bar-by-bar backtest engine for long-only spot trading (no leverage, no shorts).

Timing rules (no look-ahead):
  * Signals are decided at the CLOSE of bar i using data up to bar i only.
  * Entries and signal exits fill at the OPEN of bar i+1, plus slippage.
  * A protective stop is live from the moment of entry. If a bar's low touches
    it, the position exits at the stop, or at the bar's open if price gapped
    through (worse fill). On the entry bar itself the fill is the stop price.
  * Fees are charged on the notional of every buy and every sell.
  * Cash earns nothing (conservative).

Sizing:
  * "full": the strategy's target exposure (0..1 of equity).
  * "risk": exposure is capped so that hitting the stop loses at most
    risk_cap of equity (money rule 5: 5% per trade). Gaps can still lose more;
    the engine records the actual loss so that shows up in the results.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Costs:
    fee: float    # per side, fraction of notional (0.0095 = 0.95%)
    slip: float   # per side, fraction of price

    @property
    def label(self) -> str:
        return f"fee{self.fee*100:.2f}%+slip{self.slip*100:.2f}%"


@dataclass
class Signals:
    enter: np.ndarray          # bool, decided at close i -> enter at open i+1 (if flat)
    exit: np.ndarray           # bool, decided at close i -> exit at open i+1 (if long)
    stop_dist: np.ndarray      # price distance from entry to stop, measured at close i; nan = no stop
    target: np.ndarray         # desired exposure 0..1 at entry
    trail: bool = False        # trailing stop: stop = max(stop, close - stop_dist) each close
    max_hold: int | None = None  # bars held before a time exit


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_px: float
    exit_px: float
    frac: float          # exposure taken at entry (fraction of equity)
    risk_frac: float     # planned loss at stop as a fraction of equity (nan if no stop)
    pnl_pct: float       # change in equity from this trade, as % of equity at entry
    r_mult: float        # pnl / planned risk (nan if no stop)
    bars: int
    reason: str          # signal | stop | time | end


@dataclass
class Result:
    equity: pd.Series
    trades: list[Trade] = field(default_factory=list)
    fees_paid: float = 0.0
    bars_in_market: int = 0


def run(df: pd.DataFrame, sig: Signals, costs: Costs, sizing: str = "full",
        risk_cap: float = 0.05, start_equity: float = 1000.0) -> Result:
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    idx = df.index
    n = len(df)
    if sizing not in ("full", "risk"):
        raise ValueError("sizing must be 'full' or 'risk'")

    cash = start_equity
    units = 0.0
    stop = np.nan
    entry_px = entry_eq = frac = risk_frac = 0.0
    entry_i = -1
    bars_held = 0
    pend_entry = pend_exit = False
    pend_sd = pend_tgt = np.nan
    pend_reason = "signal"
    fees = 0.0
    in_mkt = 0
    trades: list[Trade] = []
    eq = np.empty(n)

    def close_pos(i: int, px: float, reason: str) -> None:
        nonlocal cash, units, fees, stop, entry_i
        proceeds = units * px
        fee = proceeds * costs.fee
        cash += proceeds - fee
        fees += fee
        pnl = cash - entry_eq
        trades.append(Trade(idx[entry_i], idx[i], entry_px, px, frac, risk_frac,
                            pnl / entry_eq * 100.0,
                            (pnl / (entry_eq * risk_frac)) if risk_frac > 0 else np.nan,
                            i - entry_i + 1, reason))
        units = 0.0
        stop = np.nan
        entry_i = -1

    for i in range(n):
        entered_now = False
        # 1) actions decided at the previous close fill at this bar's open
        if pend_exit and units > 0:
            close_pos(i, o[i] * (1 - costs.slip), pend_reason)
        pend_exit = False
        if pend_entry and units == 0:
            fill = o[i] * (1 + costs.slip)
            tgt = float(np.clip(pend_tgt if np.isfinite(pend_tgt) else 1.0, 0.0, 1.0))
            d = pend_sd / fill if np.isfinite(pend_sd) and pend_sd > 0 else np.nan
            if sizing == "risk":
                tgt = min(tgt, risk_cap / d) if np.isfinite(d) else 0.0
            if tgt > 0:
                entry_eq = cash
                units = entry_eq * tgt / (fill * (1 + costs.fee))
                cost = units * fill
                fee = cost * costs.fee
                cash -= cost + fee
                fees += fee
                entry_px, entry_i, bars_held, frac = fill, i, 0, tgt
                stop = fill - pend_sd if np.isfinite(d) else np.nan
                risk_frac = tgt * d if np.isfinite(d) else np.nan
                entered_now = True
        pend_entry = False

        # 2) protective stop during the bar
        if units > 0 and np.isfinite(stop) and lo[i] <= stop:
            px = stop if entered_now else min(o[i], stop)
            close_pos(i, px * (1 - costs.slip), "stop")

        # 3) mark to market
        if units > 0:
            in_mkt += 1
        eq[i] = cash + units * c[i]

        # 4) decide at the close for the next bar
        if i == n - 1:
            break
        if units > 0:
            bars_held += 1
            if sig.exit[i]:
                pend_exit, pend_reason = True, "signal"
            elif sig.max_hold and bars_held >= sig.max_hold:
                pend_exit, pend_reason = True, "time"
            elif sig.trail and np.isfinite(stop) and np.isfinite(sig.stop_dist[i]):
                stop = max(stop, c[i] - sig.stop_dist[i])
        elif sig.enter[i]:
            pend_entry = True
            pend_sd, pend_tgt = sig.stop_dist[i], sig.target[i]

    if units > 0:  # close the open position at the last close for reporting
        close_pos(n - 1, c[n - 1], "end")
        eq[n - 1] = cash
    return Result(pd.Series(eq, index=idx), trades, fees, in_mkt)


# ---------------------------------------------------------------- metrics

def daily(equity: pd.Series) -> pd.Series:
    return equity.resample("1D").last().dropna()


def metrics(res: Result, n_bars: int) -> dict:
    eq = daily(res.equity)
    if len(eq) < 3:
        return {}
    r = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    total = eq.iloc[-1] / eq.iloc[0] - 1
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1 if years > 0 and eq.iloc[-1] > 0 else -1.0
    dd = (eq / eq.cummax() - 1).min()
    sd = r.std()
    down = r[r < 0].std()
    sharpe = r.mean() / sd * np.sqrt(365) if sd > 0 else 0.0
    sortino = r.mean() / down * np.sqrt(365) if down and down > 0 else 0.0
    tr = res.trades
    pnl = np.array([t.pnl_pct for t in tr]) if tr else np.array([])
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    pf = wins.sum() / -losses.sum() if losses.size and losses.sum() < 0 else (np.inf if wins.size else 0.0)
    rm = np.array([t.r_mult for t in tr if np.isfinite(t.r_mult)])
    tstat = pnl.mean() / (pnl.std(ddof=1) / np.sqrt(pnl.size)) if pnl.size > 2 and pnl.std(ddof=1) > 0 else 0.0
    worst = pnl.min() if pnl.size else 0.0
    return {
        "start": str(eq.index[0].date()), "end": str(eq.index[-1].date()), "years": round(years, 2),
        "total_return_pct": round(total * 100, 1), "cagr_pct": round(cagr * 100, 1),
        "max_dd_pct": round(dd * 100, 1), "sharpe": round(sharpe, 2), "sortino": round(sortino, 2),
        "calmar": round(cagr / abs(dd), 2) if dd < 0 else 0.0,
        "exposure_pct": round(res.bars_in_market / max(n_bars, 1) * 100, 1),
        "trades": len(tr), "win_rate_pct": round(wins.size / pnl.size * 100, 1) if pnl.size else 0.0,
        "profit_factor": round(float(pf), 2) if np.isfinite(pf) else 99.0,
        "avg_win_pct": round(float(wins.mean()), 2) if wins.size else 0.0,
        "avg_loss_pct": round(float(losses.mean()), 2) if losses.size else 0.0,
        "expectancy_pct": round(float(pnl.mean()), 3) if pnl.size else 0.0,
        "expectancy_r": round(float(rm.mean()), 3) if rm.size else None,
        "trade_tstat": round(float(tstat), 2),
        "worst_trade_pct": round(float(worst), 2),
        "worst_day_pct": round(float(r.min() * 100), 1) if len(r) else 0.0,
        "avg_bars_held": round(float(np.mean([t.bars for t in tr])), 1) if tr else 0.0,
        "fees_pct_of_start": round(res.fees_paid / eq.iloc[0] * 100, 1),
    }
