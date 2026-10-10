"""Run once: read-only Tradier sandbox connectivity check.
Railway:  python -m scripts.check_tradier   (same checks run at worker startup)
"""
import logging
import sys

from engine import config
from engine.brokers import TradierBroker
from engine.worker import connectivity_check

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

if __name__ == "__main__":
    s = config.load()
    if not s.tradier_sandbox_token:
        print("TRADIER_SANDBOX_TOKEN not set")
        sys.exit(2)
    ok = connectivity_check(TradierBroker(s.tradier_sandbox_token, live=False))
    sys.exit(0 if all(ok.values()) else 1)
