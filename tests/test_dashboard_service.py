"""Tests for the dashboard's serialized robot and microphone session."""

import unittest

from cozmo_tr.dashboard_service import (
    DashboardError,
    DashboardService,
    DashboardTurn,
)

from cozmo_tr.actions import RobotAction


class FakeRobot:
    """Collect lifecycle calls and safe actions."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.actions: list[RobotAction] = []

    def connect(self) -> None:
        self.calls.append("connect")

    def execute(self, action: RobotAction) -> None:
        self.actions.append(action)

    def close(self) -> None:
        self.calls.append("close")


class FakeTranscriber:
    """Return one deterministic Turkish transcript."""

    def __init__(self, text: str = "başını kaldır") -> None:
        self.text = text
        self.seconds: list[float] = []

    def transcribe_once(self, seconds: float) -> str:
        self.seconds.append(seconds)
        return self.text


class DashboardServiceTests(unittest.TestCase):
    """Keep one explicit robot connection behind the existing safety path."""

    def setUp(self) -> None:
        self.robot = FakeRobot()
        self.transcriber = FakeTranscriber()
        self.service = DashboardService(
            robot_factory=lambda: self.robot,
            transcriber_factory=lambda: self.transcriber,
        )

    def test_connect_is_explicit_and_idempotent(self) -> None:
        self.assertFalse(self.service.connected)
        self.service.connect()
        self.service.connect()
        self.assertTrue(self.service.connected)
        self.assertEqual(self.robot.calls, ["connect"])

    def test_execute_requires_connection_and_preserves_safety_bounds(self) -> None:
        with self.assertRaisesRegex(DashboardError, "Önce Cozmo") as caught:
            self.service.execute("ileri 999")
        self.assertEqual(caught.exception.status, 409)
        self.service.connect()
        result = self.service.execute("ileri 999")
        self.assertTrue(result.accepted)
        self.assertEqual(self.robot.actions[0].value, 150.0)

    def test_unknown_text_is_rejected_without_robot_action(self) -> None:
        self.service.connect()
        result = self.service.execute("ışınlan")
        self.assertFalse(result.accepted)
        self.assertEqual(self.robot.actions, [])

    def test_listen_returns_transcript_and_executes_one_safe_turn(self) -> None:
        self.service.connect()
        turn = self.service.listen(3.0)
        expected = DashboardTurn("başını kaldır", turn.result)
        self.assertEqual(turn, expected)
        self.assertTrue(turn.result.accepted)
        self.assertEqual(self.transcriber.seconds, [3.0])
        self.assertEqual(len(self.robot.actions), 1)

    def test_disconnect_and_close_are_idempotent(self) -> None:
        self.service.connect()
        self.service.disconnect()
        self.service.close()
        self.assertFalse(self.service.connected)
        self.assertEqual(self.robot.calls, ["connect", "close"])


if __name__ == "__main__":
    unittest.main()
