"""Tests for bounded robot actions; no hardware is used."""

import math
import unittest
from typing import cast

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
            with self.subTest(value=value), self.assertRaises(UnsafeAction):
                self.policy.enforce(RobotAction(ActionKind.MOVE, value=value))

    def test_rejects_empty_speech(self) -> None:
        with self.assertRaises(UnsafeAction):
            self.policy.enforce(RobotAction(ActionKind.SPEAK, text="   "))

    def test_clamps_head_lift_and_volume(self) -> None:
        head = self.policy.enforce(RobotAction(ActionKind.HEAD, value=200.0))
        lift = self.policy.enforce(RobotAction(ActionKind.LIFT, value=-20.0))
        volume = self.policy.enforce(RobotAction(ActionKind.VOLUME, value=150.0))
        self.assertEqual(head.value, 44.5)
        self.assertEqual(lift.value, 32.0)
        self.assertEqual(volume.value, 100.0)

    def test_accepts_named_non_motor_actions(self) -> None:
        actions = (
            RobotAction(ActionKind.LIGHTS, text="blue"),
            RobotAction(ActionKind.FACE, text="surprised"),
            RobotAction(ActionKind.CAMERA, text="capture"),
            RobotAction(ActionKind.STATUS, text="battery"),
            RobotAction(ActionKind.ROUTINE, text="dance"),
            RobotAction(ActionKind.BALL, text="play"),
            RobotAction(ActionKind.ACCESSORY, text="cube_blue"),
        )
        self.assertEqual(tuple(map(self.policy.enforce, actions)), actions)

    def test_rejects_unknown_named_actions(self) -> None:
        invalid = (
            RobotAction(ActionKind.LIGHTS, text="purple"),
            RobotAction(ActionKind.FACE, text="sleepy"),
            RobotAction(ActionKind.CAMERA, text="record"),
            RobotAction(ActionKind.ROUTINE, text="play_ball"),
            RobotAction(ActionKind.BALL, text="kick"),
            RobotAction(ActionKind.ACCESSORY, text="cube_purple"),
        )
        for action in invalid:
            with self.subTest(action=action), self.assertRaises(UnsafeAction):
                self.policy.enforce(action)

    def test_headlight_requires_boolean_number(self) -> None:
        for value in (None, -1.0, 0.5, 2.0):
            with self.subTest(value=value), self.assertRaises(UnsafeAction):
                self.policy.enforce(RobotAction(ActionKind.HEADLIGHT, value=value))

    def test_rejects_unknown_action_kind(self) -> None:
        unknown = cast(ActionKind, object())
        with self.assertRaises(UnsafeAction):
            self.policy.enforce(RobotAction(unknown))


if __name__ == "__main__":
    unittest.main()
