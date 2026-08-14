"""Tests for bounded robot actions; no hardware is used."""

import math
import unittest

from cozmo_tr.actions import ActionKind, RobotAction, SafetyPolicy, UnsafeAction


class SafetyPolicyTests(unittest.TestCase):
    """Verify every action is bounded before a robot can receive it."""

    def setUp(self) -> None:
        self.policy = SafetyPolicy()

    def test_clamps_forward_and_backward_distance(self) -> None:
        forward = RobotAction(ActionKind.MOVE, value=999.0)
        backward = RobotAction(ActionKind.MOVE, value=-999.0)
        self.assertEqual(self.policy.enforce(forward).value, 150.0)
        self.assertEqual(self.policy.enforce(backward).value, -150.0)

    def test_clamps_turn_both_directions(self) -> None:
        left = RobotAction(ActionKind.TURN, value=120.0)
        right = RobotAction(ActionKind.TURN, value=-120.0)
        self.assertEqual(self.policy.enforce(left).value, 90.0)
        self.assertEqual(self.policy.enforce(right).value, -90.0)

    def test_stop_is_preserved(self) -> None:
        action = RobotAction(ActionKind.STOP)
        self.assertEqual(self.policy.enforce(action), action)

    def test_speech_is_trimmed_and_bounded(self) -> None:
        action = RobotAction(ActionKind.SPEAK, text=" x " * 200)
        safe = self.policy.enforce(action)
        self.assertLessEqual(len(safe.text), 160)
        self.assertFalse(safe.text.startswith(" "))

    def test_rejects_missing_zero_and_non_finite_values(self) -> None:
        invalid = (None, 0.0, math.nan, math.inf)
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(UnsafeAction):
                    self.policy.enforce(RobotAction(ActionKind.MOVE, value=value))

    def test_rejects_empty_speech(self) -> None:
        with self.assertRaises(UnsafeAction):
            self.policy.enforce(RobotAction(ActionKind.SPEAK, text="   "))


if __name__ == "__main__":
    unittest.main()
