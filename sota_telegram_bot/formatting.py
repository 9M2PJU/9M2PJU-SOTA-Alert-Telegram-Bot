from __future__ import annotations

import html
from datetime import datetime

from .models import Alert, Spot


def _clean(value: str | None, fallback: str = "-") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return html.escape(text) if text else fallback


def _format_time(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%Y-%m-%d %H:%M UTC")


def format_spot(spot: Spot) -> str:
    comments = f"\nComments: {_clean(spot.comments)}" if spot.comments else ""
    activator = _clean(spot.activator_callsign or spot.callsign)
    return (
        "<b>SOTA Spot</b>\n\n"
        f"<b>{activator}</b> on <b>{_clean(spot.summit_ref)}</b>\n"
        f"{_clean(spot.summit_details)}\n\n"
        f"Freq: {_clean(spot.frequency)} MHz\n"
        f"Mode: {_clean(spot.mode)}\n"
        f"Spotted by: {_clean(spot.callsign)}\n"
        f"Time: {_format_time(spot.timestamp)}"
        f"{comments}"
    )


def format_alert(alert: Alert) -> str:
    comments = f"\nComments: {_clean(alert.comments)}" if alert.comments else ""
    return (
        "<b>SOTA Alert</b>\n\n"
        f"<b>{_clean(alert.activating_callsign)}</b> plans <b>{_clean(alert.summit_ref)}</b>\n"
        f"{_clean(alert.summit_details)}\n\n"
        f"When: {_format_time(alert.date_activated)}\n"
        f"Freq/mode: {_clean(alert.frequency)}\n"
        f"Poster: {_clean(alert.poster_callsign)}"
        f"{comments}"
    )


def help_text() -> str:
    return (
        "<b>9M2PJU SOTA Bot</b>\n\n"
        "Commands:\n"
        "/subscribe - enable notifications\n"
        "/unsubscribe - stop notifications\n"
        "/spots_on - enable spot notifications\n"
        "/spots_off - disable spot notifications\n"
        "/alerts_on - enable alert notifications\n"
        "/alerts_off - disable alert notifications\n"
        "/spots - latest matching spots\n"
        "/alerts - upcoming matching alerts\n"
        "/filter - show filters\n"
        "/filter 9M2 - set association filter\n"
        "/filter 9M6 - set association filter\n"
        "/filter callsign 9M2PJU - set callsign filter\n"
        "/filter mode CW - set mode filter\n"
        "/clearfilters - remove filters"
    )
