"""The Railway worker. One process, one loop.

Startup: log settings (redacted), check Tradier sandbox connectivity
(profile, balances, SPY quote, SPY expirations, market clock), write a
heartbeat. Then every LOOP_SECONDS: heartbeat; in market hours run each
runnable strategy, pass orders through the risk engine, send to the paper
broker, record a shadow fill, write the ledger; every SNAPSHOT_MINUTES and at
the close, push /ledger to the data branch.

Live trading is impossible here until TRADIER_LIVE_TOKEN and
LIVE_TRADING_ENABLED=true are both set in Railway by Gomes.
"""
from __future__ import annotations

import logging
import sys
import time
import traceback
from pathlib import Path

from engine import config
from engine.alerts import Alerts
from engine.brokers import TradierBroker
from engine.clock import is_close_window, is_market_hours, now_ny
from engine.datapush import DataPusher
from engine.ledger import Ledger
from engine.risk import AccountState, RiskEngine
from engine.shadow import ShadowSimulator
from strategies.registry import load_runnable

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("worker")


def connectivity_check(broker: TradierBroker) -> dict:
    """Read-only checks. Returns a dict of pass/fail per check."""
    results = {}
    try:
        p = broker.ping()
        results["profile"] = True
        log.info("CHECK profile ok: account=%s type=%s status=%s paper=%s",
                 p["account_number"], p["type"], p["status"], p["paper"])
    except Exception as e:  # noqa: BLE001
        results["profile"] = False
        log.error("CHECK profile FAILED: %s", e)
    try:
        b = broker.balances()
        results["balances"] = True
        log.info("CHECK balances ok: equity=%.2f cash=%.2f settled=%.2f", b.equity, b.cash, b.settled_cash)
    except Exception as e:  # noqa: BLE001
        results["balances"] = False
        log.error("CHECK balances FAILED: %s", e)
    try:
        q = broker.quote("SPY")
        results["quote"] = q.last > 0
        log.info("CHECK quote SPY: last=%.2f bid=%.2f ask=%.2f (delayed=%s)", q.last, q.bid, q.ask, q.delayed)
    except Exception as e:  # noqa: BLE001
        results["quote"] = False
        log.error("CHECK quote FAILED: %s", e)
    try:
        ex = broker.expirations("SPY")
        results["options_chain"] = len(ex) > 0
        log.info("CHECK SPY expirations: %d (first %s)", len(ex), ex[:3])
    except Exception as e:  # noqa: BLE001
        results["options_chain"] = False
        log.error("CHECK expirations FAILED: %s", e)
    try:
        c = broker.clock()
        results["clock"] = True
        log.info("CHECK market clock: state=%s next=%s", c.get("state"), c.get("next_change"))
    except Exception as e:  # noqa: BLE001
        results["clock"] = False
        log.error("CHECK clock FAILED: %s", e)
    passed = sum(1 for v in results.values() if v)
    log.info("RESULT: %d/%d connectivity checks passed", passed, len(results))
    return results


def account_state(broker: TradierBroker, settings: config.Settings, peak: float,
                  sod: float) -> AccountState:
    b = broker.balances()
    return AccountState(equity=b.equity, peak_equity=max(peak, b.equity),
                        start_of_day_equity=sod or b.equity, settled_cash=b.settled_cash,
                        mode=settings.mode, live_token_present=settings.live_token_present)


def main() -> int:
    settings = config.load()
    log.info("Compound City worker starting: %s", settings.redacted())
    ledger = Ledger(settings.ledger_dir)
    alerts = Alerts(settings.alert_webhook_url)
    pusher = DataPusher(settings.github_repo, settings.data_branch, settings.github_data_token)

    if not settings.tradier_sandbox_token:
        log.error("TRADIER_SANDBOX_TOKEN is not set. Add it in Railway > Variables. Idling.")
        ledger.heartbeat("missing_sandbox_token")
        while True:
            time.sleep(300)
            ledger.heartbeat("missing_sandbox_token")

    broker = TradierBroker(settings.tradier_sandbox_token, live=False)
    checks = connectivity_check(broker)
    ledger.heartbeat("started", {"checks": checks, "mode": settings.mode, "env": settings.env_name})
    if not all(checks.values()):
        alerts.send(f"Compound City bot: connectivity checks failed {checks}")

    risk = RiskEngine()
    shadow = ShadowSimulator(slippage_bps=settings.shadow_slippage_bps)
    strategies = load_runnable()
    log.info("runnable strategies: %s", [s.name for s in strategies] or "none yet")

    peak = 0.0
    sod = 0.0
    sod_date = None
    last_push = 0.0
    pushed_close_for = None
    last_run: dict[str, float] = {}

    while True:
        loop_start = time.time()
        try:
            t = now_ny()
            in_hours = is_market_hours(t)
            if sod_date != t.date():
                sod_date, sod = t.date(), 0.0
            if in_hours:
                acct = account_state(broker, settings, peak, sod)
                peak = acct.peak_equity
                sod = sod or acct.equity
                positions = broker.positions()
                for strat in strategies:
                    if loop_start - last_run.get(strat.name, 0) < strat.cfg.interval_seconds:
                        continue
                    last_run[strat.name] = loop_start
                    quotes = {s: broker.quote(s) for s in strat.cfg.symbols}
                    for order in strat.on_tick(quotes, positions, settings.mode):
                        order.mode = "paper" if settings.mode != "live" else order.mode
                        v = risk.check(order, acct)
                        ledger.trade("risk_check", order.mode, strat.name, order.symbol, order.side,
                                     order.qty, max_loss=order.max_loss, cost=order.cost,
                                     note=("allowed" if v.allowed else "; ".join(v.reasons)))
                        if not v.allowed:
                            log.warning("order blocked [%s]: %s", strat.name, v.reasons)
                            continue
                        res = broker.place(order)
                        ledger.trade("order", order.mode, strat.name, order.symbol, order.side,
                                     order.qty, source=broker.name, order_id=res.order_id or "",
                                     note=res.status)
                        sf = shadow.fill(order)
                        if sf:
                            ledger.trade("shadow_fill", order.mode, strat.name, sf.symbol, sf.side,
                                         sf.qty, price=sf.price, source=sf.source, note=sf.note)
                ledger.write_json("snapshot.json", {
                    "equity": acct.equity, "settled_cash": acct.settled_cash, "mode": settings.mode,
                    "positions": positions, "strategies": [s.status() for s in strategies],
                    "peak_equity": peak, "start_of_day_equity": sod})
            ledger.heartbeat("ok", {"market_open": in_hours, "mode": settings.mode,
                                    "strategies": [s.name for s in strategies]})

            due = (loop_start - last_push) >= settings.snapshot_minutes * 60
            close_due = is_close_window(t) and pushed_close_for != t.date()
            if (in_hours and due) or close_due or last_push == 0:
                pusher.push_dir(Path(settings.ledger_dir), "ledger",
                                f"snapshot {t.isoformat(timespec='minutes')}")
                last_push = loop_start
                if close_due:
                    pushed_close_for = t.date()
        except Exception as e:  # noqa: BLE001
            log.error("loop error: %s\n%s", e, traceback.format_exc())
            ledger.heartbeat("error", {"error": str(e)})
            alerts.send(f"Compound City bot loop error: {e}")
        time.sleep(max(1.0, settings.loop_seconds - (time.time() - loop_start)))


if __name__ == "__main__":
    sys.exit(main())
