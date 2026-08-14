"""Integration tests for one text turn through fake robot I/O."""

import unittest
from dataclasses import dataclass, field

from cozmo_tr.actions import ActionKind, RobotAction, UnsafeAction
from cozmo_tr.orchestrator import TurnService


@dataclass
class FakeRobot:
    """Collect actions without touching physical hardware."""

    actions: list[RobotAction] = field(default_factory=list)

    def execute(self, action: RobotAction) -> None:
        """Record one already-safe action."""
        self.actions.append(action)


class RejectingPolicy:
    """Reject every action to cover the safety failure boundary."""

    def enforce(self, _action: RobotAction) -> RobotAction:
        """Raise the same domain failure as a real policy."""
        raise UnsafeAction("test rejection")


class TurnServiceTests(unittest.TestCase):
    """Ensure a turn cannot bypass parsing or safety."""

    def test_executes_clamped_action(self) -> None:
        robot = FakeRobot()
        result = TurnService(robot).handle("ileri 999")
        self.assertTrue(result.accepted)
        self.assertEqual(robot.actions, [RobotAction(ActionKind.MOVE, value=150.0)])

    def test_unknown_text_does_not_reach_robot(self) -> None:
        robot = FakeRobot()
        result = TurnService(robot).handle("bunu anlayamazsın")
        self.assertFalse(result.accepted)
        self.assertEqual(robot.actions, [])
        self.assertIn("Anlayamadım", result.message)

    def test_unsafe_action_does_not_reach_robot(self) -> None:
        robot = FakeRobot()
        result = TurnService(robot, RejectingPolicy()).handle("ileri")
        self.assertFalse(result.accepted)
        self.assertEqual(robot.actions, [])
        self.assertIn("güvenli değil", result.message)

    def test_expands_dance_into_safe_primitives(self) -> None:
        robot = FakeRobot()
        result = TurnService(robot).handle("dans et")
        self.assertTrue(result.accepted)
        self.assertGreater(len(robot.actions), 3)
        self.assertTrue(
            all(action.kind is not ActionKind.ROUTINE for action in robot.actions)
        )
        self.assertEqual(robot.actions[-1], RobotAction(ActionKind.STOP))

    def test_greeting_includes_turkish_speech(self) -> None:
        robot = FakeRobot()
        result = TurnService(robot).handle("selam ver")
        self.assertTrue(result.accepted)
        speech = [
            action.text for action in robot.actions if action.kind is ActionKind.SPEAK
        ]
        self.assertEqual(speech, ["Selam!"])


if __name__ == "__main__":
    unittest.main()
