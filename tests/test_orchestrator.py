"""Integration tests for one text turn through fake robot I/O."""

import unittest
from dataclasses import dataclass, field

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.orchestrator import TurnService


@dataclass
class FakeRobot:
    """Collect actions without touching physical hardware."""

    actions: list[RobotAction] = field(default_factory=list)

    def execute(self, action: RobotAction) -> None:
        """Record one already-safe action."""
        self.actions.append(action)


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


if __name__ == "__main__":
    unittest.main()
