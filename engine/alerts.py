"""Phone alerts through a webhook (Discord-style JSON {"content": ...}).
Used for problems and, later, Robinhood trade tickets. Silent if unset."""
from __future__ import annotations

import logging

import requests

log = logging.getLogger("alerts")


class Alerts:
    def __init__(self, url: str | None):
        self.url = url

    def send(self, text: str) -> bool:
        if not self.url:
            log.info("ALERT (no webhook set): %s", text)
            return False
        try:
            r = requests.post(self.url, json={"content": text[:1900]}, timeout=10)
            return r.status_code < 300
        except Exception as e:  # noqa: BLE001
            log.warning("alert failed: %s", e)
            return False
