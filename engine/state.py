"""Persistent risk + sizing state, kept in ledger/risk_state.json.

The file is pushed to branch `data` with the rest of /ledger and restored at
startup, so a Railway restart or redeploy does NOT reset:
  * peak equity (drawdown kill switch)
  * start-of-day equity (daily loss stop)
  * the kill switch itself (sticky until a human resets it)
  * the paper baseline (virtual paper equity)

Virtual paper equity (decided 2026-10-13, Vivek chose $1,000 whole shares):
the Tradier sandbox account holds $100,000, so paper sizing uses
    virtual_equity  = PAPER_EQUITY + (sandbox_equity  - baseline_equity)
    virtual_settled = PAPER_EQUITY + (sandbox_settled - baseline_settled)
i.e. a $1,000 account that gains/loses exactly the dollars the sandbox does.

Kill switch reset: Vivek sets Railway variable KILL_SWITCH_RESET to today's
New York date (YYYY-MM-DD) and the bot restarts; any other value is ignored,
so a value left behind can't silently re-arm trading on a later day.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RiskState:
    peak_equity: float = 0.0
    sod_equity: float = 0.0
    sod_date: Optional[str] = None
    kill_switch_on: bool = False
    kill_switch_reason: str = ""
    kill_switch_at: Optional[str] = None
    paper_start_equity: Optional[float] = None
    paper_baseline_equity: Optional[float] = None
    paper_baseline_settled: Optional[float] = None
    paper_baseline_at: Optional[str] = None

    # ----- persistence --------------------------------------------------
    @classmethod
    def load(cls, path: Path) -> "RiskState":
        if not path.exists():
            return cls()
        try:
            raw = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return cls()
        known = {k: raw[k] for k in cls.__dataclass_fields__ if k in raw}
        return cls(**known)

    def save(self, path: Path) -> None:
        data = {"as_of": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                **asdict(self)}
        path.write_text(json.dumps(data, indent=2))

    # ----- paper baseline -----------------------------------------------
    def ensure_paper_baseline(self, paper_equity: float, sandbox_equity: float,
                              sandbox_settled: float) -> bool:
        """Set the baseline once (or again if PAPER_EQUITY changed).
        Returns True if it was (re)set."""
        if (self.paper_baseline_equity is not None
                and self.paper_start_equity == paper_equity):
            return False
        self.paper_start_equity = paper_equity
        self.paper_baseline_equity = sandbox_equity
        self.paper_baseline_settled = sandbox_settled
        self.paper_baseline_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        # a new paper account starts with a clean peak / day
        self.peak_equity = paper_equity
        self.sod_equity = 0.0
        self.sod_date = None
        return True

    def virtual(self, sandbox_equity: float, sandbox_settled: float) -> tuple[float, float]:
        assert self.paper_start_equity is not None and self.paper_baseline_equity is not None
        eq = self.paper_start_equity + (sandbox_equity - self.paper_baseline_equity)
        st = self.paper_start_equity + (sandbox_settled - (self.paper_baseline_settled or 0.0))
        return round(eq, 2), round(min(st, eq), 2)

    # ----- daily / peak tracking -----------------------------------------
    def roll_day(self, today: str, equity: float) -> None:
        if self.sod_date != today:
            self.sod_date = today
            self.sod_equity = equity

    def update_peak(self, equity: float) -> None:
        self.peak_equity = max(self.peak_equity, equity)

    def drawdown(self, equity: float) -> float:
        return 0.0 if self.peak_equity <= 0 else (self.peak_equity - equity) / self.peak_equity

    # ----- kill switch ------------------------------------------------------
    def trip_kill_switch(self, reason: str) -> bool:
        if self.kill_switch_on:
            return False
        self.kill_switch_on = True
        self.kill_switch_reason = reason
        self.kill_switch_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        return True

    def try_reset_kill_switch(self, reset_value: Optional[str], today_ny: str) -> bool:
        if self.kill_switch_on and reset_value and reset_value.strip() == today_ny:
            self.kill_switch_on = False
            self.kill_switch_reason = f"reset by human on {today_ny}"
            self.kill_switch_at = None
            return True
        return False
