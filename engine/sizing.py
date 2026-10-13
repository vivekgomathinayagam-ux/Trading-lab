"""Is a setup tradeable at a given live account size?

Paper runs at PAPER_EQUITY ($1,000, whole shares). Each setup also reports
whether the same trade could be placed at LIVE_EQUITY (default $1,000 — the
expected account size when Gomes actually goes live, not the $50 money-rule
cap on his own money going in), so the city can show "tradeable at live
size: yes/no" honestly.
"""
from __future__ import annotations

from engine.risk import DEFAULT_CAPS, RiskCaps


def max_units(equity: float, settled_cash: float, loss_per_unit: float, cost_per_unit: float,
              fractional: bool = False, caps: RiskCaps = DEFAULT_CAPS) -> float:
    if loss_per_unit <= 0 or cost_per_unit < 0 or equity <= 0:
        return 0.0
    by_loss = equity * caps.max_loss_per_trade_pct / loss_per_unit
    by_cash = settled_cash / cost_per_unit if cost_per_unit > 0 else by_loss
    units = min(by_loss, by_cash)
    return round(units, 6) if fractional else float(int(units))


def tradeable_at(equity: float, loss_per_unit: float, cost_per_unit: float,
                 fractional: bool = False, caps: RiskCaps = DEFAULT_CAPS) -> dict:
    """Assumes the whole account is settled cash. Returns a small report."""
    units = max_units(equity, equity, loss_per_unit, cost_per_unit, fractional, caps)
    ok = units > 0
    cap = equity * caps.max_loss_per_trade_pct
    if ok:
        why = f"{units:g} units fit the {caps.max_loss_per_trade_pct:.0%} cap and cash"
    else:
        reasons = []
        if not fractional and loss_per_unit > cap:
            reasons.append(f"one unit risks ${loss_per_unit:,.2f}, cap is ${cap:,.2f}")
        if not fractional and cost_per_unit > equity:
            reasons.append(f"one unit costs ${cost_per_unit:,.2f}, account is ${equity:,.2f}")
        why = "; ".join(reasons) or "no size fits"
    return {"equity": equity, "tradeable": ok, "units": units, "fractional": fractional,
            "why": why}
