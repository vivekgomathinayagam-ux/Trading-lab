"""Risk engine for Compound City.

Every order, paper or live, passes through `RiskEngine.check()` before it can
reach a broker. The engine is deterministic and has no network access. It
returns a `Verdict`; an order is sent only when `verdict.allowed` is True.

Caps (from the project money rules; changing them needs Gomes's yes in chat):
  * MAX_LOSS_PER_TRADE_PCT  = 5%  of live equity (per order's worst case)
  * DAILY_LOSS_STOP_PCT     = 10% of start-of-day equity -> no new live entries today
  * DRAWDOWN_KILL_PCT       = 30% from peak equity -> all live trading stops
                                until a human resets the kill switch
  * No margin, no naked short options, nothing with undefined risk
  * Whole shares and whole contracts only
  * Cash account: an order can't use more than settled cash
  * Live orders are impossible unless mode == "live" AND a live token exists

Paper orders are sized against the live-size equity (rule 7) and go through
the same caps so paper results reflect what live would allow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

AssetType = Literal["equity", "option", "spread"]
Side = Literal["buy", "sell", "buy_to_open", "sell_to_open", "buy_to_close", "sell_to_close"]
Mode = Literal["paper", "live"]


@dataclass(frozen=True)
class RiskCaps:
    max_loss_per_trade_pct: float = 0.05
    daily_loss_stop_pct: float = 0.10
    drawdown_kill_pct: float = 0.30


DEFAULT_CAPS = RiskCaps()


@dataclass
class OptionLeg:
    symbol: str          # OCC symbol, e.g. SPY251017C00580000
    side: Side           # buy_to_open / sell_to_open / ...
    qty: int
    strike: float
    right: Literal["call", "put"]
    expiry: str          # YYYY-MM-DD


@dataclass
class Order:
    """A proposed order. `max_loss` is the worst-case dollar loss of the
    whole position including the stop (equity) or the structure (options).
    `cost` is the cash the order consumes (debit) or 0 for a credit."""
    strategy: str
    symbol: str
    asset_type: AssetType
    side: Side
    qty: float
    max_loss: float
    cost: float
    mode: Mode = "paper"
    legs: list[OptionLeg] = field(default_factory=list)
    uses_margin: bool = False
    is_entry: bool = True          # False for closing / reducing orders
    fractional_ok: bool = False    # True only once broker confirms fractional support


@dataclass
class AccountState:
    """What the engine needs to know about the account right now."""
    equity: float                  # current equity (live size, also used for paper)
    peak_equity: float             # highest equity seen (for drawdown)
    start_of_day_equity: float
    settled_cash: float
    mode: Mode = "paper"
    live_token_present: bool = False
    kill_switch_on: bool = False   # sticky until a human resets it


@dataclass
class Verdict:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.allowed


class RiskEngine:
    def __init__(self, caps: RiskCaps = DEFAULT_CAPS):
        self.caps = caps

    # ----- helpers -------------------------------------------------------
    @staticmethod
    def _is_whole(x: float) -> bool:
        return abs(x - round(x)) < 1e-9

    @staticmethod
    def _undefined_risk(order: Order) -> bool:
        """True if any short option leg is not covered by a long leg of the
        same right with qty >= short qty (i.e. naked). Equity shorts also
        count as undefined risk."""
        if order.asset_type == "equity":
            return order.side in ("sell", "sell_to_open") and order.is_entry
        if not order.legs:
            # a single option with sell_to_open and no legs = naked
            return order.side == "sell_to_open"
        for right in ("call", "put"):
            short = sum(l.qty for l in order.legs if l.right == right and l.side == "sell_to_open")
            long_ = sum(l.qty for l in order.legs if l.right == right and l.side == "buy_to_open")
            if short > long_:
                return True
        return False

    # ----- main entry point ---------------------------------------------
    def check(self, order: Order, acct: AccountState) -> Verdict:
        reasons: list[str] = []
        checks: dict[str, bool] = {}

        # 0. Live orders need live mode AND a live token. Paper never sends live.
        live_ok = not (order.mode == "live" and (acct.mode != "live" or not acct.live_token_present))
        checks["live_gate"] = live_ok
        if not live_ok:
            reasons.append("live order refused: account not in live mode or no live token")

        # 1. Kill switch (30% drawdown) -> nothing live, entries or exits of new risk
        dd = 0.0 if acct.peak_equity <= 0 else (acct.peak_equity - acct.equity) / acct.peak_equity
        kill = acct.kill_switch_on or dd >= self.caps.drawdown_kill_pct
        kill_ok = not (kill and order.mode == "live")
        checks["drawdown_kill"] = kill_ok
        if not kill_ok:
            reasons.append(
                f"kill switch: drawdown {dd:.1%} >= {self.caps.drawdown_kill_pct:.0%} "
                "(or switch already on); all live trading stopped until reviewed")

        # 2. Daily loss stop (10%) -> no new live entries today (exits still allowed)
        day_loss = 0.0 if acct.start_of_day_equity <= 0 else (
            (acct.start_of_day_equity - acct.equity) / acct.start_of_day_equity)
        daily_ok = not (order.mode == "live" and order.is_entry and day_loss >= self.caps.daily_loss_stop_pct)
        checks["daily_loss_stop"] = daily_ok
        if not daily_ok:
            reasons.append(
                f"daily loss {day_loss:.1%} >= {self.caps.daily_loss_stop_pct:.0%}: no new live entries today")

        # 3. Per-trade max loss (5% of equity) - applies to paper and live entries
        cap_dollars = acct.equity * self.caps.max_loss_per_trade_pct
        per_trade_ok = (not order.is_entry) or (order.max_loss <= cap_dollars + 1e-9)
        checks["max_loss_per_trade"] = per_trade_ok
        if not per_trade_ok:
            reasons.append(
                f"max loss ${order.max_loss:,.2f} > {self.caps.max_loss_per_trade_pct:.0%} of equity "
                f"(${cap_dollars:,.2f}); account too small for this setup")

        # 4. No margin
        margin_ok = not order.uses_margin
        checks["no_margin"] = margin_ok
        if not margin_ok:
            reasons.append("margin not allowed")

        # 5. No undefined risk / naked shorts
        defined_ok = not self._undefined_risk(order)
        checks["defined_risk"] = defined_ok
        if not defined_ok:
            reasons.append("undefined risk (naked short) not allowed")

        # 6. Whole shares / contracts
        whole_ok = order.fractional_ok or self._is_whole(order.qty)
        if order.legs:
            whole_ok = whole_ok and all(self._is_whole(l.qty) for l in order.legs)
        checks["whole_units"] = whole_ok
        if not whole_ok:
            reasons.append("fractional quantity not allowed until broker confirms support")

        # 7. Cash account: don't spend unsettled money
        cash_ok = (not order.is_entry) or (order.cost <= acct.settled_cash + 1e-9)
        checks["settled_cash"] = cash_ok
        if not cash_ok:
            reasons.append(f"cost ${order.cost:,.2f} > settled cash ${acct.settled_cash:,.2f}")

        # 8. Sanity
        sane = order.qty > 0 and order.max_loss >= 0 and order.cost >= 0
        checks["sane"] = sane
        if not sane:
            reasons.append("order has non-positive qty or negative loss/cost")

        return Verdict(allowed=all(checks.values()), reasons=reasons, checks=checks)

    # ----- sizing helper -------------------------------------------------
    def max_qty(self, acct: AccountState, loss_per_unit: float, cost_per_unit: float) -> int:
        """Largest whole quantity whose worst-case loss fits the per-trade cap
        and whose cost fits settled cash. Returns 0 if nothing fits."""
        if loss_per_unit <= 0 or cost_per_unit < 0:
            return 0
        by_loss = int((acct.equity * self.caps.max_loss_per_trade_pct) // loss_per_unit)
        by_cash = int(acct.settled_cash // cost_per_unit) if cost_per_unit > 0 else by_loss
        return max(0, min(by_loss, by_cash))
