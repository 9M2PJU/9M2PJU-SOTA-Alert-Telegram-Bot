from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .models import Alert, Spot


class SotawatchError(RuntimeError):
    pass


class SotawatchClient:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds
        self.spots_url = "https://api2.sota.org.uk/api/spots/-1/all"
        self.alerts_url = "https://api2.sota.org.uk/api/alerts"

    def _get_json(self, url: str) -> list[dict[str, Any]]:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "9M2PJU-SOTA-Bot/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise SotawatchError(f"Could not fetch {url}: {exc}") from exc

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise SotawatchError(f"SOTAwatch returned invalid JSON from {url}") from exc
        if not isinstance(data, list):
            raise SotawatchError(f"SOTAwatch returned unexpected payload from {url}")
        return data

    def fetch_spots(self) -> list[Spot]:
        return [Spot.from_api(item) for item in self._get_json(self.spots_url)]

    def fetch_alerts(self) -> list[Alert]:
        return [Alert.from_api(item) for item in self._get_json(self.alerts_url)]
