"""Tests for honest machine-readable capability status."""

import unittest

from cozmo_tr.capabilities import CapabilityState, capability_by_id, command_lines


class CapabilityCatalogTests(unittest.TestCase):
    """Distinguish implemented software from hardware-pending behavior."""

    def test_ball_stays_visible_as_hardware_pending(self) -> None:
        ball = capability_by_id("ball_play")
        self.assertEqual(ball.state, CapabilityState.HARDWARE_PENDING)
        self.assertIn("topla oyna", ball.commands)

    def test_current_direct_effects_are_listed(self) -> None:
        for capability_id in ("motion", "speech", "head_lift", "lights", "camera"):
            with self.subTest(capability_id=capability_id):
                capability = capability_by_id(capability_id)
                self.assertTrue(capability.commands)

    def test_command_lines_are_human_readable(self) -> None:
        rendered = "\n".join(command_lines())
        self.assertIn("[hardware_pending] Top oyunu", rendered)
        self.assertIn("[experimental] Hareket", rendered)

    def test_unknown_capability_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            capability_by_id("teleport")


if __name__ == "__main__":
    unittest.main()
