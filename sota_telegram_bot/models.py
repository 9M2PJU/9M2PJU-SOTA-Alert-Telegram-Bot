from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def parse_sota_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class Spot:
    id: int
    timestamp: datetime | None
    callsign: str
    association_code: str
    summit_code: str
    activator_callsign: str
    activator_name: str
    frequency: str
    mode: str
    summit_details: str
    comments: str

    @property
    def summit_ref(self) -> str:
        return f"{self.association_code}/{self.summit_code}"

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Spot":
        return cls(
            id=int(data["id"]),
            timestamp=parse_sota_datetime(data.get("timeStamp")),
            callsign=str(data.get("callsign") or ""),
            association_code=str(data.get("associationCode") or ""),
            summit_code=str(data.get("summitCode") or ""),
            activator_callsign=str(data.get("activatorCallsign") or ""),
            activator_name=str(data.get("activatorName") or ""),
            frequency=str(data.get("frequency") or ""),
            mode=str(data.get("mode") or ""),
            summit_details=str(data.get("summitDetails") or ""),
            comments=str(data.get("comments") or ""),
        )


@dataclass(frozen=True)
class Alert:
    id: int
    timestamp: datetime | None
    date_activated: datetime | None
    association_code: str
    summit_code: str
    summit_details: str
    frequency: str
    comments: str
    activating_callsign: str
    activator_name: str
    poster_callsign: str

    @property
    def summit_ref(self) -> str:
        return f"{self.association_code}/{self.summit_code}"

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Alert":
        return cls(
            id=int(data["id"]),
            timestamp=parse_sota_datetime(data.get("timeStamp")),
            date_activated=parse_sota_datetime(data.get("dateActivated")),
            association_code=str(data.get("associationCode") or ""),
            summit_code=str(data.get("summitCode") or ""),
            summit_details=str(data.get("summitDetails") or ""),
            frequency=str(data.get("frequency") or ""),
            comments=str(data.get("comments") or ""),
            activating_callsign=str(data.get("activatingCallsign") or ""),
            activator_name=str(data.get("activatorName") or ""),
            poster_callsign=str(data.get("posterCallsign") or ""),
        )


@dataclass(frozen=True)
class Subscriber:
    chat_id: int
    is_active: bool
    notify_spots: bool
    notify_alerts: bool
    association_filter: str
    callsign_filter: str
    mode_filter: str
