import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from engine import config
from engine.brokers.base import Balances
from engine.sizing import max_units, tradeable_at
from engine.state import RiskState
from engine.worker import build_account_state


class FakeBroker:
    def __init__(self, equity, settled):
        self.equity, self.settled = equity, settled

    def balances(self):
        return Balances(self.equity, self.equity, self.settled, self.settled, {})


def paper_settings(**env):
    base = {"TRADIER_SANDBOX_TOKEN": "x", "PAPER_EQUITY": "1000"}
    base.update(env)
    with unittest.mock.patch.dict(os.environ, base, clear=True):
        return config.load()


class VirtualPaperEquity(unittest.TestCase):
    def test_sandbox_100k_becomes_1000(self):
        st = RiskState()
        acct = build_account_state(FakeBroker(100_000, 100_000), paper_settings(), st, "2026-10-13")
        self.assertEqual(acct.equity, 1000.0)
        self.assertEqual(acct.settled_cash, 1000.0)
        self.assertEqual(acct.mode, "paper")

    def test_dollar_pnl_carries_through(self):
        st = RiskState()
        s = paper_settings()
        build_account_state(FakeBroker(100_000, 100_000), s, st, "2026-10-13")
        acct = build_account_state(FakeBroker(99_950, 99_950), s, st, "2026-10-13")
        self.assertEqual(acct.equity, 950.0)       # lost $50 of a $1,000 account
        self.assertEqual(acct.peak_equity, 1000.0)

    def test_buying_reduces_virtual_settled_cash(self):
        st = RiskState()
        s = paper_settings()
        build_account_state(FakeBroker(100_000, 100_000), s, st, "2026-10-13")
        acct = build_account_state(FakeBroker(100_000, 99_222), s, st, "2026-10-13")  # bought 1 SPY
        self.assertEqual(acct.settled_cash, 222.0)

    def test_changing_paper_equity_resets_baseline(self):
        st = RiskState()
        build_account_state(FakeBroker(100_000, 100_000), paper_settings(), st, "2026-10-13")
        acct = build_account_state(FakeBroker(99_000, 99_000), paper_settings(PAPER_EQUITY="2000"),
                                   st, "2026-10-14")
        self.assertEqual(acct.equity, 2000.0)


class KillSwitchPersistence(unittest.TestCase):
    def test_trips_at_30pct_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "risk_state.json"
            st = RiskState()
            s = paper_settings()
            build_account_state(FakeBroker(100_000, 100_000), s, st, "2026-10-13")
            acct = build_account_state(FakeBroker(99_700, 99_700), s, st, "2026-10-13")  # 30% of $1k
            self.assertTrue(acct.kill_switch_on)
            st.save(path)
            # "restart": reload from disk, equity recovers, switch must stay on
            st2 = RiskState.load(path)
            acct2 = build_account_state(FakeBroker(100_000, 100_000), s, st2, "2026-10-14")
            self.assertTrue(acct2.kill_switch_on)
            self.assertEqual(acct2.peak_equity, 1000.0)

    def test_reset_needs_todays_date_exactly(self):
        st = RiskState()
        st.trip_kill_switch("test")
        self.assertFalse(st.try_reset_kill_switch("true", "2026-10-13"))
        self.assertFalse(st.try_reset_kill_switch("2026-10-12", "2026-10-13"))  # stale value
        self.assertTrue(st.kill_switch_on)
        self.assertTrue(st.try_reset_kill_switch("2026-10-13", "2026-10-13"))
        self.assertFalse(st.kill_switch_on)

    def test_start_of_day_rolls_once_per_day(self):
        st = RiskState()
        s = paper_settings()
        build_account_state(FakeBroker(100_000, 100_000), s, st, "2026-10-13")
        build_account_state(FakeBroker(99_950, 99_950), s, st, "2026-10-13")
        self.assertEqual(st.sod_equity, 1000.0)
        build_account_state(FakeBroker(99_950, 99_950), s, st, "2026-10-14")
        self.assertEqual(st.sod_equity, 950.0)

    def test_corrupt_state_file_starts_clean(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "risk_state.json"
            p.write_text("{not json")
            self.assertFalse(RiskState.load(p).kill_switch_on)


class TradeableAtLiveSize(unittest.TestCase):
    def test_spy_whole_share_not_tradeable_at_50(self):
        r = tradeable_at(50.0, loss_per_unit=4.0, cost_per_unit=778.0)
        self.assertFalse(r["tradeable"])
        self.assertIn("costs", r["why"])

    def test_spy_fractional_tradeable_at_50(self):
        r = tradeable_at(50.0, loss_per_unit=4.0, cost_per_unit=778.0, fractional=True)
        self.assertTrue(r["tradeable"])
        self.assertGreater(r["units"], 0)

    def test_spread_risk_too_big_at_50(self):
        r = tradeable_at(50.0, loss_per_unit=60.0, cost_per_unit=60.0)
        self.assertFalse(r["tradeable"])
        self.assertIn("risks", r["why"])

    def test_spy_one_share_fits_1000(self):
        self.assertEqual(max_units(1000.0, 1000.0, 4.0, 778.0), 1.0)


if __name__ == "__main__":
    unittest.main()
