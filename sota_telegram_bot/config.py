from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    db_path: str = "data/bot.sqlite3"
    spots_poll_seconds: int = 45
    alerts_poll_seconds: int = 300
    request_timeout_seconds: int = 20
    bootstrap_existing_items: bool = True


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    return Settings(
        telegram_bot_token=token,
        db_path=os.getenv("SOTA_DB_PATH", "data/bot.sqlite3"),
        spots_poll_seconds=_env_int("SOTA_SPOTS_POLL_SECONDS", 45),
        alerts_poll_seconds=_env_int("SOTA_ALERTS_POLL_SECONDS", 300),
        request_timeout_seconds=_env_int("SOTA_REQUEST_TIMEOUT_SECONDS", 20),
        bootstrap_existing_items=os.getenv("SOTA_BOOTSTRAP_EXISTING_ITEMS", "1") != "0",
    )
