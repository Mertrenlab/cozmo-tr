"""Tests for one bounded ball interaction through fake camera and robot ports."""

import unittest
from collections.abc import Iterable

from cozmo_tr.ball_session import BallSession

from cozmo_tr.actions import ActionKind, RobotAction, SafetyPolicy

Pixel = tuple[int, int, int]


class FakeFrame:
    """Return a centered red target or a dark frame."""

    def __init__(self, has_ball: bool) -> None:
        self.size = (20, 20)
        self._pixels = [
            (220, 20, 20)
            if has_ball and 6 <= index % 20 <= 13 and 6 <= index // 20 <= 13
            else (10, 10, 10)
            for index in range(400)
        ]

    def convert(self, _mode: str) -> "FakeFrame":
        return self

    def getdata(self) -> Iterable[Pixel]:
        return self._pixels


class FakeExecutor:
    """Collect primitive actions instead of touching hardware."""

    def __init__(self) -> None:
        self.actions: list[RobotAction] = []

    def execute(self, _client: object, action: RobotAction) -> None:
        self.actions.append(action)


class RecordingPolicy:
    """Record that every planned action crossed the real safety policy."""

    def __init__(self) -> None:
        self.actions: list[RobotAction] = []
        self._policy = SafetyPolicy()

    def enforce(self, action: RobotAction) -> RobotAction:
        self.actions.append(action)
        return self._policy.enforce(action)


class BallSessionTests(unittest.TestCase):
    """Execute one finite camera decision and stop without hidden loops."""

    def test_play_executes_safe_push_and_return_plan(self) -> None:
        executor = FakeExecutor()
        policy = RecordingPolicy()
        session = BallSession(
            executor, capture=lambda _client: FakeFrame(True), policy=policy
        )
        session.play(object(), "play")
        self.assertEqual(
            executor.actions,
            [
                RobotAction(ActionKind.MOVE, 30.0),
                RobotAction(ActionKind.MOVE, -30.0),
                RobotAction(ActionKind.STOP),
            ],
        )
        self.assertEqual(policy.actions, executor.actions)

    def test_missing_ball_stops_and_explains(self) -> None:
        executor = FakeExecutor()
        session = BallSession(executor, capture=lambda _client: FakeFrame(False))
        session.play(object(), "find")
        self.assertEqual(
            executor.actions,
            [
                RobotAction(ActionKind.STOP),
                RobotAction(ActionKind.SPEAK, text="Topu göremedim."),
            ],
        )


if __name__ == "__main__":
    unittest.main()
