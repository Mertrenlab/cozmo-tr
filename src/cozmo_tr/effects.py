"""Map safe primitive actions onto the verified PyCozmo client surface.

Responsible for: finite hardware calls, local TTS, face and camera effects.
Not responsible for: parsing, safety policy, connection lifecycle, or routines.
"""

import logging
import tempfile
from collections.abc import Callable, Mapping
from importlib import import_module
from math import radians
from pathlib import Path
from typing import Protocol

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.capture import CameraClient, capture_photo
from cozmo_tr.errors import RobotUnavailable
from cozmo_tr.faces import render_face
from cozmo_tr.tts import MacSayTts, WavSpec

DRIVE_SPEED_MMPS = 75.0
TURN_RATE_AT_FULL_SPEED = 130.0
FULL_SPEED_MMPS = 100.0
FACE_DURATION_SECONDS = 2.0
MAX_VOLUME_LEVEL = 65_535

logger = logging.getLogger(__name__)


class SpeechSynthesizer(Protocol):
    """Create one Cozmo-compatible WAV from Turkish text."""

    def synthesize(self, text: str, output: Path) -> WavSpec: ...


class EffectClient(CameraClient, Protocol):
    """Describe the verified direct-control methods used by this adapter."""

    battery_voltage: float

    def drive_wheels(self, left: float, right: float, duration: float) -> None: ...
    def stop_all_motors(self) -> None: ...
    def play_audio(self, path: str) -> None: ...
    def set_head_angle(self, angle: float) -> None: ...
    def set_lift_height(self, height: float) -> None: ...
    def set_all_backpack_lights(self, light: object) -> None: ...
    def set_backpack_lights_off(self) -> None: ...
    def set_head_light(self, enabled: bool) -> None: ...
    def display_image(self, image: object, duration: float) -> None: ...
    def set_volume(self, level: int) -> None: ...


EffectHandler = Callable[[EffectClient, RobotAction], None]
FaceRenderer = Callable[[str], object]
PhotoCapture = Callable[[CameraClient], object]


class RobotEffects:
    """Execute safe primitive actions against one connected PyCozmo client."""

    def __init__(
        self,
        tts: SpeechSynthesizer | None = None,
        lights: Mapping[str, object] | None = None,
        face_renderer: FaceRenderer = render_face,
        photo_capture: PhotoCapture = capture_photo,
    ) -> None:
        self._tts = tts or MacSayTts()
        self._lights = lights or _load_lights()
        self._face_renderer = face_renderer
        self._photo_capture = photo_capture

    def execute(self, client: EffectClient, action: RobotAction) -> None:
        """Perform one finite effect or raise RobotUnavailable with context."""
        handler = self._handlers().get(action.kind)
        if handler is None:
            raise RobotUnavailable(f"İlkel olmayan eylem: {action.kind}")
        try:
            handler(client, action)
        except RobotUnavailable:
            raise
        except Exception as error:
            raise RobotUnavailable(f"{action.kind} eylemi uygulanamadı") from error

    def _handlers(self) -> dict[ActionKind, EffectHandler]:
        return {
            ActionKind.STOP: self._stop,
            ActionKind.MOVE: self._move,
            ActionKind.TURN: self._turn,
            ActionKind.SPEAK: self._speak,
            ActionKind.HEAD: self._head,
            ActionKind.LIFT: self._lift,
            ActionKind.LIGHTS: self._set_lights,
            ActionKind.HEADLIGHT: self._headlight,
            ActionKind.FACE: self._face,
            ActionKind.CAMERA: self._camera,
            ActionKind.STATUS: self._status,
            ActionKind.VOLUME: self._volume,
        }

    @staticmethod
    def _stop(client: EffectClient, _action: RobotAction) -> None:
        client.stop_all_motors()

    @staticmethod
    def _move(client: EffectClient, action: RobotAction) -> None:
        value = _required_value(action)
        direction = 1.0 if value > 0 else -1.0
        duration = abs(value) / DRIVE_SPEED_MMPS
        client.drive_wheels(
            direction * DRIVE_SPEED_MMPS, direction * DRIVE_SPEED_MMPS, duration
        )

    @staticmethod
    def _turn(client: EffectClient, action: RobotAction) -> None:
        value = _required_value(action)
        direction = 1.0 if value > 0 else -1.0
        rate = TURN_RATE_AT_FULL_SPEED * DRIVE_SPEED_MMPS / FULL_SPEED_MMPS
        client.drive_wheels(
            -direction * DRIVE_SPEED_MMPS,
            direction * DRIVE_SPEED_MMPS,
            abs(value) / rate,
        )

    def _speak(self, client: EffectClient, action: RobotAction) -> None:
        self._play_speech(client, action.text)

    @staticmethod
    def _head(client: EffectClient, action: RobotAction) -> None:
        client.set_head_angle(radians(_required_value(action)))

    @staticmethod
    def _lift(client: EffectClient, action: RobotAction) -> None:
        client.set_lift_height(_required_value(action))

    def _set_lights(self, client: EffectClient, action: RobotAction) -> None:
        if action.text == "off":
            client.set_backpack_lights_off()
            return
        client.set_all_backpack_lights(self._lights[action.text])

    @staticmethod
    def _headlight(client: EffectClient, action: RobotAction) -> None:
        client.set_head_light(_required_value(action) == 1.0)

    def _face(self, client: EffectClient, action: RobotAction) -> None:
        client.display_image(self._face_renderer(action.text), FACE_DURATION_SECONDS)

    def _camera(self, client: EffectClient, _action: RobotAction) -> None:
        path = self._photo_capture(client)
        logger.info("camera_capture_saved", extra={"path": str(path)})

    def _status(self, client: EffectClient, _action: RobotAction) -> None:
        self._play_speech(client, f"Pil voltajım {client.battery_voltage:.1f} volt.")

    @staticmethod
    def _volume(client: EffectClient, action: RobotAction) -> None:
        percent = _required_value(action)
        client.set_volume(round(MAX_VOLUME_LEVEL * percent / 100.0))

    def _play_speech(self, client: EffectClient, text: str) -> None:
        with tempfile.TemporaryDirectory(prefix="cozmo-tr-") as directory:
            output = Path(directory) / "speech.wav"
            self._tts.synthesize(text, output)
            client.play_audio(str(output))


def _required_value(action: RobotAction) -> float:
    if action.value is None:
        raise RobotUnavailable("Güvenli eylemde sayısal değer eksik")
    return action.value


def _load_lights() -> dict[str, object]:
    module = import_module("pycozmo.lights")
    return {
        "red": module.red_light,
        "green": module.green_light,
        "blue": module.blue_light,
        "white": module.white_light,
    }
