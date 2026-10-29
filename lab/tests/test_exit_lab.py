"""Exit-lab mechanics on a tiny synthetic day (no network)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from lab.floor.exit_lab import SymData, VARS, run_exit
from strategies.daytrade.core import Bar

NY = ZoneInfo("America/New_York")


def day(prices):
    """prices: list of (o,h,l,c) one per minute from 09:30."""
    t0 = datetime(2026, 10, 20, 9, 30, tzinfo=NY)
    return [Bar(t0 + timedelta(minutes=i), *p, 1000) for i, p in enumerate(prices)]


def flat(n, px=100.0):
    return [(px, px, px, px)] * n


def test_fixed_tp_fills_at_level_and_costs():
    bars = day(flat(5) + [(100, 101.2, 100, 101)] + flat(384, 101))
    sd = SymData("SPY", bars)
    r = run_exit(sd, 5, 100.0, VARS["A_tp1"], False, entry_slip_in_px=False, fee=0.0)
    assert r["reason"] == "target"
    assert abs(r["ret"] - (1.01 * (1 - 0.0002) - 1) * 100) < 1e-6   # target is +1% from the slipped fill; sell slips once


def test_stop_beats_target_on_same_bar():
    bars = day(flat(5) + [(100, 106, 97, 100)] + flat(384))
    sd = SymData("SPY", bars)
    r = run_exit(sd, 5, 100.0, VARS["BASE"], False, entry_slip_in_px=False, fee=0.0)
    assert r["reason"] == "stop" and r["ret"] < -2.4


def test_trail_uses_prior_high_only():
    # bar 6 makes a new high 102 and dips to 101.4 in the same bar: the stop it tests is from the PRIOR high (101)
    bars = day(flat(5) + [(100, 101, 100, 101), (101, 102, 101.4, 101.5)] + flat(383, 101.5))
    sd = SymData("SPY", bars)
    r = run_exit(sd, 5, 100.0, VARS["B_trail1"], False, entry_slip_in_px=False, fee=0.0)
    assert r["reason"] == "eod"            # 1% below prior high 101 is 99.99; the dip to 101.4 does not hit it


def test_partial_then_rest_to_eod():
    bars = day(flat(5) + [(100, 101.1, 100, 101)] + flat(384, 100.5))
    sd = SymData("SPY", bars)
    r = run_exit(sd, 5, 100.0, VARS["C_half@1"], False, entry_slip_in_px=False, fee=0.0)
    assert r["partial"] and r["reason"] == "eod"
    assert 0.5 * 1.0 - 0.2 < r["ret"] < 0.5 * 1.0 + 0.5
