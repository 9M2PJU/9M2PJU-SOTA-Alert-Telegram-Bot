from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sota_telegram_bot.formatting import format_alert, format_spot
from sota_telegram_bot.models import Alert, Spot


class FormattingTests(unittest.TestCase):
    def test_spot_escapes_html(self) -> None:
        spot = Spot(
            id=1,
            timestamp=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            callsign="N0CALL",
            association_code="9M",
            summit_code="XX-001",
            activator_callsign="9M2PJU/P",
            activator_name="",
            frequency="14.285",
            mode="SSB",
            summit_details="Test <Summit>",
            comments="5 < 10",
        )
        message = format_spot(spot)
        self.assertIn("Test &lt;Summit&gt;", message)
        self.assertIn("5 &lt; 10", message)

    def test_alert_contains_activation_time(self) -> None:
        alert = Alert(
            id=1,
            timestamp=None,
            date_activated=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
            association_code="9M",
            summit_code="XX-001",
            summit_details="Test Summit",
            frequency="14-cw",
            comments="",
            activating_callsign="9M2PJU/P",
            activator_name="",
            poster_callsign="9M2PJU",
        )
        self.assertIn("2026-07-01 12:00 UTC", format_alert(alert))


if __name__ == "__main__":
    unittest.main()
