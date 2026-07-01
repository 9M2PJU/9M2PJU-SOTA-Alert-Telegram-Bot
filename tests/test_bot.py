from __future__ import annotations

import unittest

from sota_telegram_bot.commands import parse_filter_args


class BotCommandTests(unittest.TestCase):
    def test_single_filter_argument_defaults_to_association(self) -> None:
        self.assertEqual(parse_filter_args(["9M2"]), ("association", "9M2"))
        self.assertEqual(parse_filter_args(["9M6"]), ("association", "9M6"))

    def test_explicit_filter_arguments_still_work(self) -> None:
        self.assertEqual(parse_filter_args(["callsign", "9M2PJU"]), ("callsign", "9M2PJU"))
        self.assertEqual(parse_filter_args(["mode", "CW"]), ("mode", "CW"))

    def test_empty_filter_arguments(self) -> None:
        self.assertIsNone(parse_filter_args([]))


if __name__ == "__main__":
    unittest.main()
