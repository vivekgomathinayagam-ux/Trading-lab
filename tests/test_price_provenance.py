"""Vivek's approved fixes (2026-10-26): price provenance logging, Skylit cross-check,
backtest-vs-paper exit price recording, and the Yahoo-down fallback. None of these
may change a fill price or a signal in normal operation."""
import csv
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from engine.daytrade_runner import DayTradeRunner
from engine.ledger import Ledger
from engine.quotecheck import SkylitSpot, age_seconds, pct_diff
from engine.risk import RiskEngine
from strategies.daytrade.core import ORB
from tests.test_daytrade_runner import DAY, FakeBroker, FakeMD, make_day


class MetaMD(FakeMD):
    """FakeMD that also reports Yahoo-style quote metadata; can be switched off (outage)."""
    def __init__(self, history, today, quote_lag_s=5):
        super().__init__(history, today)
        self.quote_lag_s = quote_lag_s
        self.last_meta = {}
        self.down = False

    def bars(self, sym, rng="1d", now=None):
        if self.down and rng == "1d":
            raise ConnectionError("yahoo down")
        out = super().bars(sym, rng, now)
        if now is not None:
            self.last_meta[sym] = {"quote_epoch": now.timestamp() - self.quote_lag_s,
                                   "delayed_by": 0, "fetched_at": now}
        return out


class FakeSpot:
    def __init__(self, offset_pct=0.0, configured=True, per_symbol=None):
        self.offset_pct, self._conf = offset_pct, configured
        self.per_symbol = per_symbol or {}
        self.status = "ok" if configured else "unconfigured"
        self.calls = 0
        self.md = None

    @property
    def configured(self):
        return self._conf

    def spots(self, symbols):
        self.calls += 1
        out = {}
        for s in symbols:
            px = self.md.prices.get(s) if self.md else None
            if px:
                off = self.per_symbol.get(s, self.offset_pct)
                out[s] = {"spot": px * (1 + off / 100), "as_of": "t"}
        return out


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        hist = []
        for k in range(4):
            hist += make_day(DAY - timedelta(days=k + 1), [100.0] * 390, [1000.0] * 390)
        hist.sort(key=lambda b: b.t)
        closes = [100.0] * 20 + [101.0] + [101.2 + 0.25 * i for i in range(40)] + [111.0] * 329
        vols = [1000.0] * 20 + [9000.0] + [1000.0] * 369
        self.hist, self.today = hist, make_day(DAY, closes, vols)

    def run_day(self, spot=None, quote_lag_s=5, until=70, folder=None):
        folder = folder or self.dir
        md = MetaMD(self.hist, self.today, quote_lag_s)
        if spot is not None:
            md.prices = {}
            orig = md.bars

            def bars(sym, rng="1d", now=None):
                b, px = orig(sym, rng, now)
                if px:
                    md.prices[sym] = px
                return b, px
            md.bars = bars
            spot.md = md
        broker = FakeBroker()
        r = DayTradeRunner(Ledger(str(folder)), broker, RiskEngine(), md, folder,
                           symbols=["SPY"], rules=[ORB()], spot=spot)
        for i in range(1, until):
            r.step(DAY + timedelta(minutes=i, seconds=5))
        return r, md, broker

    def fills(self, folder=None):
        return list(csv.DictReader(((folder or self.dir) / "daytrade_fills.csv").open()))


class TestProvenance(Base):
    def test_every_entry_and_exit_has_quote_and_bar_times(self):
        self.run_day(spot=FakeSpot())
        rows = self.fills()
        self.assertEqual([r["kind"] for r in rows], ["entry", "exit"])
        for r in rows:
            self.assertTrue(r["quote_time"])
            self.assertTrue(r["signal_bar_start"])
            self.assertTrue(r["bot_time"])
            self.assertEqual(r["price_source"], "yahoo_rt")
            self.assertEqual(r["quote_stale"], "False")
            self.assertEqual(r["evaluation"], "preliminary")
            self.assertGreaterEqual(float(r["quote_age_s"]), 0)

    def test_quote_older_than_90s_is_flagged(self):
        self.run_day(spot=FakeSpot(), quote_lag_s=120)
        self.assertTrue(all(r["quote_stale"] == "True" for r in self.fills()))

    def test_exit_records_backtest_rule_price_next_to_paper_price(self):
        self.run_day(spot=FakeSpot())
        ex = self.fills()[-1]
        self.assertEqual(ex["reason"], "target")
        self.assertNotEqual(ex["rule_px"], "")          # the target level the backtest would use
        self.assertNotEqual(ex["paper_vs_rule_pct"], "")
        self.assertAlmostEqual(float(ex["fill_px"]), float(ex["raw_px"]) * (1 - 0.0002), places=3)


class TestCrossCheck(Base):
    def test_matching_prices_not_flagged(self):
        self.run_day(spot=FakeSpot(offset_pct=0.01))
        for r in self.fills():
            self.assertEqual(r["skylit_status"], "ok")
            self.assertEqual(r["skylit_flag"], "False")
            self.assertTrue(r["skylit_all_diffs"])

    def test_difference_above_005pct_is_flagged(self):
        self.run_day(spot=FakeSpot(offset_pct=0.2))
        self.assertTrue(all(r["skylit_flag"] == "True" for r in self.fills()))

    def test_flag_looks_only_at_the_traded_etf(self):
        # SPY (traded) matches; another ETF is far off: logged for information, not flagged
        self.run_day(spot=FakeSpot(per_symbol={"SPY": 0.01, "SPXU": 0.5}))
        for r in self.fills():
            self.assertEqual(r["skylit_flag"], "False")
            self.assertEqual(r["skylit_diff_pct"], "-0.01")   # Yahoo vs Skylit
        # and the traded ETF off -> flagged
        folder = Path(tempfile.mkdtemp())
        self.run_day(spot=FakeSpot(per_symbol={"SPY": 0.2}), folder=folder)
        self.assertTrue(all(r["skylit_flag"] == "True" for r in self.fills(folder)))

    def test_unconfigured_skylit_logs_without_crashing(self):
        self.run_day(spot=FakeSpot(configured=False))
        self.assertTrue(all(r["skylit_status"] == "unconfigured" for r in self.fills()))
        self.run_day(spot=None, folder=Path(tempfile.mkdtemp()))   # no client at all

    def test_one_skylit_call_per_step_at_most(self):
        sp = FakeSpot()
        self.run_day(spot=sp)
        self.assertLessEqual(sp.calls, 2)   # one entry step + one exit step


class TestNoExecutionChange(Base):
    def test_fill_prices_identical_with_and_without_checks(self):
        a, b = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.run_day(spot=None, folder=a)
        self.run_day(spot=FakeSpot(offset_pct=0.3), quote_lag_s=500, folder=b)
        ta = list(csv.DictReader((a / "daytrade_trades.csv").open()))
        tb = list(csv.DictReader((b / "daytrade_trades.csv").open()))
        strip = lambda rows: [{k: v for k, v in r.items() if not k.endswith("_t")} for r in rows]
        self.assertEqual(strip(ta), strip(tb))


class TestFallback(Base):
    def test_yahoo_down_values_with_skylit_and_blocks_entries(self):
        sp = FakeSpot()
        r, md, broker = self.run_day(spot=sp, until=25)       # entered on the breakout
        d = r.desks["orb_vol"]
        self.assertIsNotNone(d.pos)
        md.down = True
        r.step(DAY + timedelta(minutes=25, seconds=5))
        self.assertEqual(r.price_src.get("SPY"), "skylit_fallback")
        self.assertTrue(r.feed["entries_paused"])
        self.assertEqual(r.feed["yahoo_down"], ["SPY"])

    def test_no_entry_while_feed_down_and_no_stale_entry_after(self):
        sp = FakeSpot()
        r, md, broker = self.run_day(spot=sp, until=2)
        md.down = True
        for i in range(2, 40):                                 # breakout happens during the outage
            r.step(DAY + timedelta(minutes=i, seconds=5))
        self.assertEqual(broker.orders, [])
        md.down = False
        r.step(DAY + timedelta(minutes=40, seconds=5))         # catch-up bars are stale
        self.assertEqual(broker.orders, [])
        self.assertFalse(r.feed["entries_paused"])


class TestSkylitClient(unittest.TestCase):
    def resp(self, code, payload=None):
        m = mock.Mock(status_code=code)
        m.json.return_value = payload or {}
        return m

    def test_parses_spots_and_sends_bearer(self):
        c = SkylitSpot("k")
        payload = {"data": {"symbols": [{"symbol": "SPY", "spot": 765.1, "asOf": "x"},
                                        {"symbol": "QQQ", "spot": 714.4, "asOf": "y"}]}}
        with mock.patch.object(c.s, "get", return_value=self.resp(200, payload)) as g:
            out = c.spots(["SPY", "QQQ"])
        self.assertEqual(out["SPY"]["spot"], 765.1)
        self.assertEqual(c.status, "ok")
        self.assertEqual(g.call_args.kwargs["headers"]["Authorization"], "Bearer k")

    def test_http_error_returns_empty(self):
        c = SkylitSpot("k")
        with mock.patch.object(c.s, "get", return_value=self.resp(429)):
            self.assertEqual(c.spots(["SPY"]), {})
        self.assertEqual(c.status, "http 429")

    def test_no_key_makes_no_request(self):
        c = SkylitSpot(None)
        with mock.patch.object(c.s, "get") as g:
            self.assertEqual(c.spots(["SPY"]), {})
        g.assert_not_called()

    def test_helpers(self):
        self.assertEqual(pct_diff(100.05, 100.0), 0.05)
        self.assertIsNone(pct_diff(None, 1))
        self.assertEqual(age_seconds(1000, datetime.fromtimestamp(1095, timezone.utc)), 95.0)


if __name__ == "__main__":
    unittest.main()
