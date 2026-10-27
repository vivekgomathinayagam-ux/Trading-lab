"""The Railway worker. One process, one loop.

Startup:
  1. log settings (redacted)
  2. restore /ledger from branch `data` (Railway has no volume)
  3. load risk_state.json (peak, start-of-day, kill switch, paper baseline)
  4. read-only Tradier sandbox connectivity check
Then every LOOP_SECONDS: heartbeat; in market hours run each runnable
strategy, pass orders through the risk engine, send to the paper broker,
record a shadow fill, write the ledger. Push /ledger to branch `data` every
SNAPSHOT_MINUTES in market hours, at the close, and every
OFFHOURS_PUSH_MINUTES otherwise (so the city sees the bot is alive).

Paper sizing: virtual $PAPER_EQUITY account (see engine/state.py), not the
sandbox's $100k. Live trading is impossible here until TRADIER_LIVE_TOKEN and
LIVE_TRADING_ENABLED=true are both set in Railway by Vivek.
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
from engine.daytrade_runner import DayTradeRunner, enabled as daytrade_enabled
from engine.datapush import DataPusher
from engine.marketdata import YahooBars
from engine.quotecheck import SkylitSpot
from engine.ledger import Ledger
from engine.risk import DEFAULT_CAPS, AccountState, RiskEngine
from engine.shadow import ShadowSimulator
from engine.state import RiskState
from strategies.registry import load_runnable

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("worker")

STATE_FILE = "risk_state.json"


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


def build_account_state(broker: TradierBroker, settings: config.Settings, st: RiskState,
                        today: str) -> AccountState:
    """Real balances in live mode; virtual $PAPER_EQUITY account in paper mode.
    Updates peak / start-of-day / kill switch in `st` (caller saves it)."""
    b = broker.balances()
    if settings.mode == "live":
        equity, settled = b.equity, b.settled_cash
    else:
        if st.ensure_paper_baseline(settings.paper_equity, b.equity, b.settled_cash):
            log.info("paper baseline set: virtual $%.2f account (sandbox equity %.2f)",
                     settings.paper_equity, b.equity)
        equity, settled = st.virtual(b.equity, b.settled_cash)
    st.roll_day(today, equity)
    st.update_peak(equity)
    dd = st.drawdown(equity)
    if dd >= DEFAULT_CAPS.drawdown_kill_pct and st.trip_kill_switch(
            f"drawdown {dd:.1%} from peak ${st.peak_equity:,.2f}"):
        log.error("KILL SWITCH TRIPPED: %s", st.kill_switch_reason)
    return AccountState(equity=equity, peak_equity=st.peak_equity,
                        start_of_day_equity=st.sod_equity, settled_cash=settled,
                        mode=settings.mode, live_token_present=settings.live_token_present,
                        kill_switch_on=st.kill_switch_on)


def main() -> int:
    settings = config.load()
    log.info("Compound City worker starting: %s", settings.redacted())
    ledger_dir = Path(settings.ledger_dir)
    alerts = Alerts(settings.alert_webhook_url)
    pusher = DataPusher(settings.github_repo, settings.data_branch, settings.github_data_token)

    # 1. restore ledger + risk state BEFORE the ledger writer creates empty files
    try:
        pusher.pull_dir(ledger_dir, "ledger")
    except Exception as e:  # noqa: BLE001
        log.error("ledger restore failed (continuing with local files): %s", e)
        alerts.send(f"Compound City bot: ledger restore failed: {e}")
    ledger = Ledger(settings.ledger_dir)
    state_path = ledger_dir / STATE_FILE
    st = RiskState.load(state_path)
    today = now_ny().date().isoformat()
    if st.try_reset_kill_switch(settings.kill_switch_reset, today):
        log.warning("kill switch RESET by KILL_SWITCH_RESET=%s; remove that variable", today)
        ledger.trade("kill_switch_reset", settings.mode, "-", "-", "-", 0, note=f"reset {today}")
    if st.kill_switch_on:
        log.error("kill switch is ON (%s); live entries and exits blocked until reset",
                  st.kill_switch_reason)
    st.save(state_path)

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
    daytrade = None
    if daytrade_enabled():
        spot = SkylitSpot(settings.skylit_api_key)
        daytrade = DayTradeRunner(ledger, broker, risk, YahooBars(), ledger_dir,
                                  equity=settings.paper_equity, spot=spot)
        log.info("day-trade desks on paper: %s", [d["label"] for d in daytrade.status()])
        if spot.configured:   # read-only check, 1 Skylit credit; never logs the key
            got = spot.spots(daytrade.symbols)
            log.info("CHECK skylit spot: %s, %d/%d symbols %s", spot.status, len(got),
                     len(daytrade.symbols), {k: v["spot"] for k, v in got.items()})
        else:
            log.warning("SKYLIT_API_KEY not set: fill prices are logged without the Skylit "
                        "cross-check, and there is no fallback if Yahoo fails")
        try:   # proves the live 1-minute feed works now, not at the next open
            daytrade.warmup()
        except Exception as e:  # noqa: BLE001
            log.error("day-trade warm-up failed (will retry at the open): %s", e)
            alerts.send(f"Compound City: day-trade 1-minute feed failed at startup: {e}")
    desk_names = [s.name for s in strategies] + ([d["desk"] for d in daytrade.status()] if daytrade else [])

    last_push = 0.0
    pushed_close_for = None
    last_run: dict[str, float] = {}
    kill_alerted = st.kill_switch_on

    while True:
        loop_start = time.time()
        try:
            t = now_ny()
            in_hours = is_market_hours(t)
            acct = None
            if in_hours:
                acct = build_account_state(broker, settings, st, t.date().isoformat())
                st.save(state_path)
                if st.kill_switch_on and not kill_alerted:
                    alerts.send(f"Compound City KILL SWITCH ON: {st.kill_switch_reason}")
                    kill_alerted = True
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
                if daytrade:
                    try:
                        daytrade.step(t)
                    except Exception as e:  # noqa: BLE001  (a desk bug must not stop the bot)
                        log.error("day-trade step error: %s\n%s", e, traceback.format_exc())
                        ledger.heartbeat("daytrade_error", {"error": str(e)})
                ledger.write_json("snapshot.json", {
                    "mode": settings.mode, "equity": acct.equity, "settled_cash": acct.settled_cash,
                    "peak_equity": st.peak_equity, "start_of_day_equity": st.sod_equity,
                    "drawdown": round(st.drawdown(acct.equity), 4),
                    "kill_switch_on": st.kill_switch_on, "paper_equity_start": st.paper_start_equity,
                    "positions": positions, "strategies": [s.status() for s in strategies],
                    "daytrade_desks": daytrade.status() if daytrade else []})
            ledger.heartbeat("ok", {"market_open": in_hours, "mode": settings.mode,
                                    "kill_switch_on": st.kill_switch_on,
                                    "strategies": desk_names})

            since = loop_start - last_push
            due_in_hours = in_hours and since >= settings.snapshot_minutes * 60
            due_off_hours = (not in_hours) and since >= settings.offhours_push_minutes * 60
            close_due = is_close_window(t) and pushed_close_for != t.date()
            if due_in_hours or due_off_hours or close_due or last_push == 0:
                pusher.push_dir(ledger_dir, "ledger",
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
