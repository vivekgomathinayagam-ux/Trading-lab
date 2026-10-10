"""Settings. Secrets are read ONLY from environment variables set in Railway.
Nothing here is ever logged in full. Variable NAMES (Gomes types the values):

  TRADIER_SANDBOX_TOKEN      required  Tradier paper (sandbox) access token
  ALERT_WEBHOOK_URL          optional  Discord/webhook URL for phone alerts
  GITHUB_DATA_TOKEN          optional  fine-grained GitHub token, Contents: read/write
                                       on the trading-lab repo only; used to push
                                       snapshots to the "data" branch
  TRADIER_LIVE_TOKEN         LATER     only when Gomes decides to go live
  LIVE_TRADING_ENABLED       LATER     must be exactly "true" as well

Non-secret settings have defaults below and can be overridden the same way.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    tradier_sandbox_token: str | None
    tradier_live_token: str | None
    live_trading_enabled: bool
    alert_webhook_url: str | None
    github_data_token: str | None
    github_repo: str
    data_branch: str
    ledger_dir: str
    loop_seconds: int
    snapshot_minutes: int
    shadow_slippage_bps: float
    env_name: str

    @property
    def live_token_present(self) -> bool:
        return bool(self.tradier_live_token)

    @property
    def mode(self) -> str:
        # Live only if BOTH the token exists and the flag is on. Otherwise paper.
        return "live" if (self.live_token_present and self.live_trading_enabled) else "paper"

    def redacted(self) -> dict:
        return {
            "mode": self.mode,
            "sandbox_token": "set" if self.tradier_sandbox_token else "MISSING",
            "live_token": "set" if self.tradier_live_token else "absent",
            "live_trading_enabled": self.live_trading_enabled,
            "alert_webhook": "set" if self.alert_webhook_url else "absent",
            "github_data_token": "set" if self.github_data_token else "absent",
            "github_repo": self.github_repo,
            "data_branch": self.data_branch,
            "loop_seconds": self.loop_seconds,
            "snapshot_minutes": self.snapshot_minutes,
        }


def load() -> Settings:
    return Settings(
        tradier_sandbox_token=_env("TRADIER_SANDBOX_TOKEN"),
        tradier_live_token=_env("TRADIER_LIVE_TOKEN"),
        live_trading_enabled=(_env("LIVE_TRADING_ENABLED", "false") or "").lower() == "true",
        alert_webhook_url=_env("ALERT_WEBHOOK_URL"),
        github_data_token=_env("GITHUB_DATA_TOKEN"),
        github_repo=_env("GITHUB_REPO", "vivekgomathinayagam-ux/Trading-lab"),
        data_branch=_env("DATA_BRANCH", "data"),
        ledger_dir=_env("LEDGER_DIR", "ledger"),
        loop_seconds=int(_env("LOOP_SECONDS", "60")),
        snapshot_minutes=int(_env("SNAPSHOT_MINUTES", "15")),
        shadow_slippage_bps=float(_env("SHADOW_SLIPPAGE_BPS", "2")),
        env_name=_env("RAILWAY_ENVIRONMENT_NAME", "local"),
    )
