"""Alpaca paper adapter: paper-only locks, whole shares, client ids, marketable limits."""
import unittest
from unittest import mock

from engine.brokers.alpaca_paper import (DATA_URL, LIVE_URL_FORBIDDEN, PAPER_URL,
                                         AlpacaPaperBroker)
from engine.risk import Order


def resp(code=200, j=None):
    r = mock.Mock(status_code=code, text="{}" if j is not None else "")
    r.json.return_value = j if j is not None else {}
    r.raise_for_status = mock.Mock()
    return r


class T(unittest.TestCase):
    def mk(self):
        s = mock.Mock()
        s.headers = {}
        s.request.return_value = resp(200, {"id": "abc", "status": "accepted"})
        s.get.return_value = resp(200, {"status": "ACTIVE"})
        return AlpacaPaperBroker("k", "s", session=s), s

    def order(self, **kw):
        base = dict(strategy="news_scalp", symbol="AAPL", asset_type="equity", side="buy",
                    qty=4, max_loss=5.0, cost=900.0, mode="paper")
        base.update(kw)
        return Order(**base)

    def test_live_url_refused(self):
        with self.assertRaises(ValueError):
            AlpacaPaperBroker("k", "s", base_url=LIVE_URL_FORBIDDEN)

    def test_live_order_refused_and_nothing_sent(self):
        b, s = self.mk()
        r = b.place(self.order(mode="live"))
        self.assertFalse(r.ok)
        s.request.assert_not_called()

    def test_options_and_fractional_refused(self):
        b, s = self.mk()
        self.assertFalse(b.place(self.order(asset_type="option")).ok)
        self.assertFalse(b.place(self.order(qty=1.5)).ok)
        s.request.assert_not_called()

    def test_limit_entry_goes_to_paper_host_with_client_id(self):
        b, s = self.mk()
        r = b.place(self.order(), limit_px=225.123, client_order_id="x1")
        self.assertTrue(r.ok)
        method, url = s.request.call_args[0]
        body = s.request.call_args[1]["json"]
        self.assertEqual((method, url), ("POST", PAPER_URL + "/v2/orders"))
        self.assertEqual(body["type"], "limit")
        self.assertEqual(body["limit_price"], "225.12")
        self.assertEqual(body["client_order_id"], "x1")
        self.assertNotIn("api.alpaca.markets/v2", url.replace("paper-api.", ""))

    def test_every_request_host_is_paper_or_data(self):
        b, s = self.mk()
        b.ping(); b.positions(); b.quote("AAPL"); b.place(self.order(), limit_px=1); b.flatten_all()
        urls = [c[0][0] for c in s.get.call_args_list] + [c[0][1] for c in s.request.call_args_list]
        for u in urls:
            self.assertTrue(u.startswith(PAPER_URL) or u.startswith(DATA_URL), u)

    def test_rejection_reported(self):
        b, s = self.mk()
        s.request.return_value = resp(422, {"message": "dup"})
        s.request.return_value.text = "dup client_order_id"
        r = b.place(self.order(), limit_px=10)
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()
