"""Tests for red-ball detection and bounded one-frame motion planning."""

import unittest
from collections.abc import Iterable

from cozmo_tr.actions import ActionKind, RobotAction, SafetyPolicy
from cozmo_tr.ball import BallObservation, detect_red_ball, plan_ball_motion

Pixel = tuple[int, int, int]


class FakeFrame:
    """Expose a tiny Pillow-compatible RGB frame surface."""

    def __init__(
        self, width: int, height: int, red_box: tuple[int, int, int, int] | None
    ) -> None:
        self.size = (width, height)
        self.mode = "RGB"
        self._pixels = _pixels(width, height, red_box)

    def convert(self, _mode: str) -> "FakeFrame":
        return self

    def getdata(self) -> Iterable[Pixel]:
        return self._pixels


def _pixels(
    width: int, height: int, red_box: tuple[int, int, int, int] | None
) -> list[Pixel]:
    result: list[Pixel] = []
    for y in range(height):
        for x in range(width):
            red = red_box is not None and _inside(x, y, red_box)
            result.append((220, 20, 20) if red else (20, 20, 20))
    return result


def _inside(x: int, y: int, box: tuple[int, int, int, int]) -> bool:
    left, top, right, bottom = box
    return left <= x <= right and top <= y <= bottom


class BallVisionTests(unittest.TestCase):
    """Reject absent targets and plan only conservative primitive actions."""

    def test_detects_centered_red_target(self) -> None:
        observation = detect_red_ball(FakeFrame(40, 30, (15, 10, 24, 19)))
        self.assertIsNotNone(observation)
        assert observation is not None
        self.assertAlmostEqual(observation.offset_x, 0.0, delta=0.06)
        self.assertGreater(observation.confidence, 0.5)

    def test_rejects_frame_without_target(self) -> None:
        self.assertIsNone(detect_red_ball(FakeFrame(40, 30, None)))

    def test_rejects_long_red_shape_that_is_not_ball_like(self) -> None:
        self.assertIsNone(detect_red_ball(FakeFrame(40, 30, (2, 12, 35, 15))))

    def test_turns_toward_left_target(self) -> None:
        observation = BallObservation(offset_x=-0.7, area_fraction=0.05, confidence=0.9)
        plan = plan_ball_motion(observation, mode="find")
        self.assertEqual(plan[0], RobotAction(ActionKind.TURN, 15.0))
        self.assertEqual(plan[-1], RobotAction(ActionKind.STOP))

    def test_turns_toward_right_target(self) -> None:
        observation = BallObservation(offset_x=0.7, area_fraction=0.05, confidence=0.9)
        plan = plan_ball_motion(observation, mode="find")
        self.assertEqual(plan[0], RobotAction(ActionKind.TURN, -15.0))

    def test_approaches_far_and_retreats_from_near_target(self) -> None:
        far = BallObservation(offset_x=0.0, area_fraction=0.02, confidence=0.9)
        near = BallObservation(offset_x=0.0, area_fraction=0.2, confidence=0.9)
        self.assertEqual(
            plan_ball_motion(far, "find")[0], RobotAction(ActionKind.MOVE, 40.0)
        )
        self.assertEqual(
            plan_ball_motion(near, "find")[0], RobotAction(ActionKind.MOVE, -30.0)
        )

    def test_centered_find_target_holds_position(self) -> None:
        centered = BallObservation(offset_x=0.0, area_fraction=0.08, confidence=0.9)
        self.assertEqual(
            plan_ball_motion(centered, "find"), (RobotAction(ActionKind.STOP),)
        )

    def test_play_pushes_and_returns_when_centered(self) -> None:
        observation = BallObservation(offset_x=0.0, area_fraction=0.08, confidence=0.9)
        plan = plan_ball_motion(observation, mode="play")
        self.assertEqual(
            plan,
            (
                RobotAction(ActionKind.MOVE, 30.0),
                RobotAction(ActionKind.MOVE, -30.0),
                RobotAction(ActionKind.STOP),
            ),
        )
        policy = SafetyPolicy()
        self.assertEqual(tuple(policy.enforce(action) for action in plan), plan)

    def test_missing_or_uncertain_target_never_moves(self) -> None:
        uncertain = BallObservation(offset_x=0.4, area_fraction=0.1, confidence=0.2)
        self.assertEqual(
            plan_ball_motion(None, "find"), (RobotAction(ActionKind.STOP),)
        )
        self.assertEqual(
            plan_ball_motion(uncertain, "play"), (RobotAction(ActionKind.STOP),)
        )

    def test_rejects_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            plan_ball_motion(None, "kick")


if __name__ == "__main__":
    unittest.main()
