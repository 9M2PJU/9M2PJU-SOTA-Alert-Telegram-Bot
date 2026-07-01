from __future__ import annotations

import tempfile
import unittest

from sota_telegram_bot.storage import Store


class StoreTests(unittest.TestCase):
    def test_subscriber_and_filters_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(f"{tmp}/bot.sqlite3")
            store.upsert_subscriber(123)
            subscriber = store.set_filter(123, "association", "9m")
            self.assertEqual(subscriber.association_filter, "9M")
            self.assertTrue(subscriber.is_active)

    def test_mark_sent_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(f"{tmp}/bot.sqlite3")
            self.assertTrue(store.mark_sent(123, "spot", 1))
            self.assertFalse(store.mark_sent(123, "spot", 1))
            self.assertTrue(store.mark_sent(123, "alert", 1))


if __name__ == "__main__":
    unittest.main()
