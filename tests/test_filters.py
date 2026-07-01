from __future__ import annotations

import unittest

from sota_telegram_bot.filters import alert_matches, spot_matches
from sota_telegram_bot.models import Alert, Spot, Subscriber


class FilterTests(unittest.TestCase):
    def subscriber(self, **overrides: object) -> Subscriber:
        data = {
            "chat_id": 123,
            "is_active": True,
            "notify_spots": True,
            "notify_alerts": True,
            "association_filter": "",
            "callsign_filter": "",
            "mode_filter": "",
        }
        data.update(overrides)
        return Subscriber(**data)

    def spot(self, **overrides: object) -> Spot:
        data = {
            "id": 1,
            "timestamp": None,
            "callsign": "9M2PJU",
            "association_code": "9M",
            "summit_code": "XX-001",
            "activator_callsign": "9M2PJU/P",
            "activator_name": "Piju",
            "frequency": "14.285",
            "mode": "SSB",
            "summit_details": "Test Summit, 1000m, 4 points",
            "comments": "",
        }
        data.update(overrides)
        return Spot(**data)

    def alert(self, **overrides: object) -> Alert:
        data = {
            "id": 1,
            "timestamp": None,
            "date_activated": None,
            "association_code": "9M",
            "summit_code": "XX-001",
            "summit_details": "Test Summit, 1000m, 4 pts",
            "frequency": "14-ssb, 145-fm",
            "comments": "",
            "activating_callsign": "9M2PJU/P",
            "activator_name": "Piju",
            "poster_callsign": "9M2PJU",
        }
        data.update(overrides)
        return Alert(**data)

    def test_spot_matches_empty_filters(self) -> None:
        self.assertTrue(spot_matches(self.subscriber(), self.spot()))

    def test_spot_association_prefix_filter(self) -> None:
        self.assertTrue(spot_matches(self.subscriber(association_filter="9"), self.spot()))
        self.assertFalse(spot_matches(self.subscriber(association_filter="W4C"), self.spot()))

    def test_spot_callsign_and_mode_filters(self) -> None:
        self.assertTrue(spot_matches(self.subscriber(callsign_filter="PJU", mode_filter="ssb"), self.spot()))
        self.assertFalse(spot_matches(self.subscriber(mode_filter="cw"), self.spot()))

    def test_inactive_subscriber_does_not_match(self) -> None:
        self.assertFalse(spot_matches(self.subscriber(is_active=False), self.spot()))
        self.assertTrue(spot_matches(self.subscriber(is_active=False), self.spot(), require_notifications=False))

    def test_spot_notification_switch(self) -> None:
        self.assertFalse(spot_matches(self.subscriber(notify_spots=False), self.spot()))
        self.assertTrue(spot_matches(self.subscriber(notify_spots=False), self.spot(), require_notifications=False))

    def test_alert_matches_frequency_mode(self) -> None:
        self.assertTrue(alert_matches(self.subscriber(mode_filter="fm"), self.alert()))
        self.assertFalse(alert_matches(self.subscriber(mode_filter="cw"), self.alert()))

    def test_alert_notification_switch(self) -> None:
        self.assertFalse(alert_matches(self.subscriber(notify_alerts=False), self.alert()))
        self.assertTrue(alert_matches(self.subscriber(notify_alerts=False), self.alert(), require_notifications=False))


if __name__ == "__main__":
    unittest.main()
