import numpy as np
from lab.scalp.backtest import HOLD, outcomes, thin


def ix(o, h, l, c):
    n = len(o)
    return dict(o=np.array(o, float), h=np.array(h, float), l=np.array(l, float), c=np.array(c, float), day=np.array(["d"] * n))


def flat(n=12, px=100.0):
    return [px] * n


def test_long_target_hit_after_entry():
    o, h, l, c = flat(), flat(), flat(), flat()
    h[2] = 100.5                                   # entry at open of bar 1 (100); target 0.3% = 100.30 hit on bar 2
    r = outcomes(ix(o, h, l, c), "long", 0.30, 0.20, cost=0.0001)[0]
    assert abs(r - (0.003 - 0.0002)) < 1e-9


def test_both_hit_same_bar_takes_the_stop():
    o, h, l, c = flat(), flat(), flat(), flat()
    h[2], l[2] = 101, 99
    r = outcomes(ix(o, h, l, c), "long", 0.30, 0.20, cost=0.0)[0]
    assert abs(r - (-0.002)) < 1e-9


def test_gap_through_stop_fills_at_open():
    o, h, l, c = flat(), flat(), flat(), flat()
    o[2], h[2], l[2], c[2] = 99.0, 99.0, 98.5, 98.6
    r = outcomes(ix(o, h, l, c), "long", 0.30, 0.20, cost=0.0)[0]
    assert abs(r - (99.0 / 100 - 1)) < 1e-9        # worse than the stop: -1.0%, not -0.2%


def test_short_mirrors_and_time_stop():
    o, h, l, c = flat(), flat(), flat(), flat()
    l[3] = 99.6                                    # short target 0.30% = 99.70
    assert abs(outcomes(ix(o, h, l, c), "short", 0.30, 0.20, cost=0.0)[0] - 0.003) < 1e-9
    o, h, l, c = flat(), flat(), flat(), flat()
    c[HOLD] = 100.1                                # nothing hit: exit at close of bar HOLD
    assert abs(outcomes(ix(o, h, l, c), "long", 0.50, 0.50, cost=0.0)[0] - 0.001) < 1e-9


def test_entry_must_fit_in_the_day_and_thin_spaces_signals():
    o = flat(); d = ix(o, o, o, o); d["day"][6:] = "e"
    r = outcomes(d, "long", 0.3, 0.2, cost=0.0)
    assert np.isnan(r[2]) and not np.isnan(r[5])   # trades that would cross into the next day are dropped
    sig = np.zeros(20, bool); sig[[2, 3, 4, 9]] = True
    assert list(np.flatnonzero(thin(sig, np.array(["d"] * 20)))) == [2, 9]
