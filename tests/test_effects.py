"""Tests for primitive PyCozmo effects through an in-memory client."""

import unittest
from pathlib import Path

from cozmo_tr.effects import RobotEffects

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.robot import RobotUnavailable
from cozmo_tr.tts import WavSpec


class FakeClient:
    """Collect the verified PyCozmo method surface used by effects."""

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.battery_voltage = 4.1

    def drive_wheels(self, left: float, right: float, duration: float) -> None:
        self.calls.append(("drive", left, right, duration))

    def stop_all_motors(self) -> None:
        self.calls.append(("stop",))

    def play_audio(self, path: str) -> None:
        self.calls.append(("audio", Path(path).suffix))

    def set_head_angle(self, angle: float) -> None:
        self.calls.append(("head", angle))

    def set_lift_height(self, height: float) -> None:
        self.calls.append(("lift", height))

    def set_all_backpack_lights(self, light: object) -> None:
        self.calls.append(("lights", light))

    def set_backpack_lights_off(self) -> None:
        self.calls.append(("lights_off",))

    def set_head_light(self, enabled: bool) -> None:
        self.calls.append(("headlight", enabled))

    def display_image(self, image: object, duration: float) -> None:
        self.calls.append(("face", image, duration))

    def set_volume(self, level: int) -> None:
        self.calls.append(("volume", level))


class FakeTts:
    """Record synthesized speech and create a placeholder WAV."""

    def __init__(self) -> None:
        self.texts: list[str] = []

    def synthesize(self, text: str, output: Path) -> WavSpec:
        self.texts.append(text)
        output.write_bytes(b"wav")
        return WavSpec(22_050, 1, 2)


class RobotEffectsTests(unittest.TestCase):
    """Map every safe primitive action to a finite client call."""

    def setUp(self) -> None:
        self.client = FakeClient()
        self.tts = FakeTts()
        self.photos: list[object] = []
        self.effects = RobotEffects(
            tts=self.tts,
            lights={"red": "RED", "off": "OFF"},
            face_renderer=lambda name: f"face:{name}",
            photo_capture=lambda client: self.photos.append(client),
        )

    def test_maps_motion_head_and_lift(self) -> None:
        self.effects.execute(self.client, RobotAction(ActionKind.MOVE, 75.0))
        self.effects.execute(self.client, RobotAction(ActionKind.TURN, -45.0))
        self.effects.execute(self.client, RobotAction(ActionKind.HEAD, 30.0))
        self.effects.execute(self.client, RobotAction(ActionKind.LIFT, 92.0))
        names = [call[0] for call in self.client.calls]
        self.assertEqual(names, ["drive", "drive", "head", "lift"])

    def test_maps_lights_face_and_volume(self) -> None:
        actions = (
            RobotAction(ActionKind.LIGHTS, text="red"),
            RobotAction(ActionKind.LIGHTS, text="off"),
            RobotAction(ActionKind.HEADLIGHT, 1.0),
            RobotAction(ActionKind.FACE, text="happy"),
            RobotAction(ActionKind.VOLUME, 50.0),
        )
        for action in actions:
            self.effects.execute(self.client, action)
        self.assertIn(("lights", "RED"), self.client.calls)
        self.assertIn(("lights_off",), self.client.calls)
        self.assertIn(("headlight", True), self.client.calls)
        self.assertIn(("face", "face:happy", 2.0), self.client.calls)
        self.assertIn(("volume", 32768), self.client.calls)

    def test_maps_speech_battery_camera_and_stop(self) -> None:
        actions = (
            RobotAction(ActionKind.SPEAK, text="Merhaba"),
            RobotAction(ActionKind.STATUS, text="battery"),
            RobotAction(ActionKind.CAMERA, text="capture"),
            RobotAction(ActionKind.STOP),
        )
        for action in actions:
            self.effects.execute(self.client, action)
        self.assertEqual(self.tts.texts, ["Merhaba", "Pil voltajım 4.1 volt."])
        self.assertEqual(self.photos, [self.client])
        self.assertIn(("stop",), self.client.calls)

    def test_rejects_unexpanded_or_unknown_action(self) -> None:
        with self.assertRaises(RobotUnavailable):
            self.effects.execute(
                self.client, RobotAction(ActionKind.ROUTINE, text="dance")
            )


if __name__ == "__main__":
    unittest.main()
