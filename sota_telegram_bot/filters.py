from __future__ import annotations

from .models import Alert, Spot, Subscriber


def _norm(value: str | None) -> str:
    return (value or "").strip().upper()


def _matches_prefix(filter_value: str, candidate: str) -> bool:
    expected = _norm(filter_value)
    if not expected:
        return True
    return _norm(candidate).startswith(expected)


def _matches_contains(filter_value: str, *candidates: str) -> bool:
    expected = _norm(filter_value)
    if not expected:
        return True
    return any(expected in _norm(candidate) for candidate in candidates)


def spot_matches(subscriber: Subscriber, spot: Spot) -> bool:
    if not subscriber.is_active or not subscriber.notify_spots:
        return False
    return (
        _matches_prefix(subscriber.association_filter, spot.association_code)
        and _matches_contains(subscriber.callsign_filter, spot.activator_callsign, spot.callsign)
        and _matches_contains(subscriber.mode_filter, spot.mode)
    )


def alert_matches(subscriber: Subscriber, alert: Alert) -> bool:
    if not subscriber.is_active or not subscriber.notify_alerts:
        return False
    return (
        _matches_prefix(subscriber.association_filter, alert.association_code)
        and _matches_contains(
            subscriber.callsign_filter,
            alert.activating_callsign,
            alert.poster_callsign,
        )
        and _matches_contains(subscriber.mode_filter, alert.frequency)
    )
