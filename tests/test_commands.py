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

    def test_parses_head_and_lift_positions(self) -> None:
        self.assert_action("başını kaldır", RobotAction(ActionKind.HEAD, 35.0))
        self.assert_action("başını indir", RobotAction(ActionKind.HEAD, -20.0))
        self.assert_action("kolunu kaldır", RobotAction(ActionKind.LIFT, 92.0))
        self.assert_action("kolunu indir", RobotAction(ActionKind.LIFT, 32.0))

    def test_parses_robot_lights(self) -> None:
        red = RobotAction(ActionKind.LIGHTS, text="red")
        self.assert_action("ışıklarını kırmızı yap", red)
        self.assert_action("ışıkları kapat", RobotAction(ActionKind.LIGHTS, text="off"))
        self.assert_action("kafa ışığını aç", RobotAction(ActionKind.HEADLIGHT, 1.0))
        self.assert_action("kafa ışığını kapat", RobotAction(ActionKind.HEADLIGHT, 0.0))

    def test_parses_face_camera_status_and_volume(self) -> None:
        self.assert_action("mutlu ol", RobotAction(ActionKind.FACE, text="happy"))
        self.assert_action("üzgün ol", RobotAction(ActionKind.FACE, text="sad"))
        self.assert_action(
            "fotoğraf çek", RobotAction(ActionKind.CAMERA, text="capture")
        )
        self.assert_action(
            "pilin ne kadar", RobotAction(ActionKind.STATUS, text="battery")
        )
        self.assert_action("sesini kıs", RobotAction(ActionKind.VOLUME, 35.0))
        self.assert_action("sesini kapat", RobotAction(ActionKind.VOLUME, 0.0))

    def test_parses_bounded_routines_and_conversation(self) -> None:
        self.assert_action("dans et", RobotAction(ActionKind.ROUTINE, text="dance"))
        self.assert_action("selam ver", RobotAction(ActionKind.ROUTINE, text="greet"))
        self.assert_action("kafanı salla", RobotAction(ActionKind.ROUTINE, text="nod"))
        self.assert_action("görüşürüz", RobotAction(ActionKind.ROUTINE, text="goodbye"))
        expected = RobotAction(ActionKind.SPEAK, text="İyiyim, teşekkür ederim.")
        self.assert_action("nasılsın", expected)

    def test_rejects_unknown_or_ambiguous_movement(self) -> None:
        self.assertIsNone(parse_command("   "))
        self.assertIsNone(parse_command("bugün hava nasıl"))
        self.assertIsNone(parse_command("ileri geri"))


if __name__ == "__main__":
    unittest.main()
