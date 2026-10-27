"""Settings. Secrets are read ONLY from environment variables set in Railway.
Nothing here is ever logged in full. Variable NAMES (Vivek types the values):

  TRADIER_SANDBOX_TOKEN      required  Tradier paper (sandbox) access token
  ALERT_WEBHOOK_URL          optional  Discord/webhook URL for phone alerts
  GITHUB_DATA_TOKEN          optional  fine-grained GitHub token, Contents: read/write
                                       on the trading-lab repo only; used to push
                                       snapshots to the "data" branch
  SKYLIT_API_KEY             optional  read-only Skylit API key (one key for the bot, made at
                                       app.skylit.ai/developer). Used only to cross-check
                                       paper fill prices and value positions if Yahoo fails.
  TRADIER_LIVE_TOKEN         LATER     only when Vivek decides to go live
  LIVE_TRADING_ENABLED       LATER     must be exactly "true" as well
  KILL_SWITCH_RESET          RARE      today's New York date (YYYY-MM-DD) to clear
                                       a tripped kill switch on the next restart

Non-secret: PAPER_EQUITY (default 1000, Vivek's choice 2026-10-13),
LIVE_EQUITY (default 1000: Vivek's live-trading capital, set 2026-10-13. Hustle
income is added to it before go-live, so raise it to the real balance then.
Used for "tradeable at live size" flags.)

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
    paper_equity: float
    live_equity: float
    kill_switch_reset: str | None
    offhours_push_minutes: int
    skylit_api_key: str | None = None

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
            "paper_equity": self.paper_equity,
            "live_equity": self.live_equity,
            "kill_switch_reset": "set" if self.kill_switch_reset else "absent",
            "skylit_api_key": "set" if self.skylit_api_key else "absent",
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
        paper_equity=float(_env("PAPER_EQUITY", "1000")),
        live_equity=float(_env("LIVE_EQUITY", "1000")),
        kill_switch_reset=_env("KILL_SWITCH_RESET"),
        offhours_push_minutes=int(_env("OFFHOURS_PUSH_MINUTES", "60")),
        skylit_api_key=_env("SKYLIT_API_KEY"),
    )
