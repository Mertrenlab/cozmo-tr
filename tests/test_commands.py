"""Tests for deterministic Turkish command parsing."""

import unittest

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.commands import parse_command


class TurkishCommandTests(unittest.TestCase):
    """Map supported Turkish phrases to typed actions without guessing."""

    def assert_action(self, phrase: str, expected: RobotAction) -> None:
        """Assert one phrase produces the exact expected action."""
        self.assertEqual(parse_command(phrase), expected)

    def test_parses_stop(self) -> None:
        self.assert_action("Cozmo, DUR!", RobotAction(ActionKind.STOP))

    def test_parses_default_and_explicit_movement(self) -> None:
        self.assert_action("ileri git", RobotAction(ActionKind.MOVE, value=50.0))
        self.assert_action("ileri 120", RobotAction(ActionKind.MOVE, value=120.0))
        self.assert_action("geri 75", RobotAction(ActionKind.MOVE, value=-75.0))

    def test_parses_turns(self) -> None:
        self.assert_action("sola dön 30", RobotAction(ActionKind.TURN, value=30.0))
        self.assert_action("sağa 45", RobotAction(ActionKind.TURN, value=-45.0))

    def test_parses_speech(self) -> None:
        expected = RobotAction(ActionKind.SPEAK, text="Merhaba dünya")
        self.assert_action("söyle Merhaba dünya", expected)

    def test_rejects_unknown_or_ambiguous_movement(self) -> None:
        self.assertIsNone(parse_command("bugün nasılsın"))
        self.assertIsNone(parse_command("ileri geri"))


if __name__ == "__main__":
    unittest.main()
