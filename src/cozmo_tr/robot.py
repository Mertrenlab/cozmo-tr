"""Adapt safe RobotAction values to direct PyCozmo hardware calls.

Responsible for: connection lifecycle, cliff stop, motors, and speaker upload.
Not responsible for: parsing, safety-policy decisions, STT, or user prompts.
"""

import tempfile
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Protocol, cast

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.tts import MacSayTts, WavSpec

DRIVE_SPEED_MMPS = 75.0
TURN_RATE_AT_FULL_SPEED = 130.0
FULL_SPEED_MMPS = 100.0
CONNECT_TIMEOUT_SECONDS = 8.0


class RobotUnavailable(RuntimeError):
    """Report a missing connection, dependency, or failed robot operation."""


class _Connection(Protocol):
    def send(self, packet: object) -> None:
        """Send one encoded protocol packet."""
        ...


class _Client(Protocol):
    conn: _Connection

    def start(self) -> None: ...
    def connect(self) -> None: ...
    def wait_for_robot(self, timeout: float = 5.0) -> None: ...
    def drive_wheels(self, left: float, right: float, duration: float) -> None: ...
    def stop_all_motors(self) -> None: ...
    def play_audio(self, path: str) -> None: ...
    def disconnect(self) -> None: ...
    def stop(self) -> None: ...


class _Tts(Protocol):
    def synthesize(self, text: str, output: Path) -> WavSpec:
        """Write one Cozmo-compatible WAV file."""
        ...


ClientFactory = Callable[[], _Client]
PacketFactory = Callable[[bool], object]


class PyCozmoRobot:
    """Manage one direct-Wi-Fi PyCozmo client behind the robot port."""

    def __init__(
        self,
        client_factory: ClientFactory | None = None,
        cliff_packet_factory: PacketFactory | None = None,
        tts: _Tts | None = None,
    ) -> None:
        """Store injectable factories; no connection occurs yet."""
        self._client_factory = client_factory
        self._packet_factory = cliff_packet_factory
        self._tts = tts or MacSayTts()
        self._client: _Client | None = None

    def connect(self) -> None:
        """Connect and enable firmware cliff stopping before any action."""
        factory = self._client_factory or _load_client_factory()
        packet_factory = self._packet_factory or _load_packet_factory()
        client = factory()
        try:
            client.start()
            client.connect()
            client.wait_for_robot(timeout=CONNECT_TIMEOUT_SECONDS)
            client.conn.send(packet_factory(True))
        except Exception as error:
            _run_shutdown(client)
            raise RobotUnavailable("Cozmo bağlantısı kurulamadı") from error
        self._client = client

    def execute(self, action: RobotAction) -> None:
        """Map one already-safe action to a finite hardware operation."""
        client = self._connected_client()
        if action.kind is ActionKind.STOP:
            client.stop_all_motors()
        elif action.kind is ActionKind.MOVE:
            self._drive(client, action)
        elif action.kind is ActionKind.TURN:
            self._turn(client, action)
        elif action.kind is ActionKind.SPEAK:
            self._speak(client, action.text)

    def close(self) -> None:
        """Stop motion and close every client layer; report any failure."""
        client = self._client
        self._client = None
        if client is None:
            return
        errors = _run_shutdown(client)
        if errors:
            raise RobotUnavailable("Cozmo güvenli kapatılamadı") from errors[0]

    def _connected_client(self) -> _Client:
        if self._client is None:
            raise RobotUnavailable("Önce Cozmo bağlantısını kurun")
        return self._client

    @staticmethod
    def _drive(client: _Client, action: RobotAction) -> None:
        value = _required_value(action)
        direction = 1.0 if value > 0 else -1.0
        duration = abs(value) / DRIVE_SPEED_MMPS
        client.drive_wheels(
            direction * DRIVE_SPEED_MMPS, direction * DRIVE_SPEED_MMPS, duration
        )

    @staticmethod
    def _turn(client: _Client, action: RobotAction) -> None:
        value = _required_value(action)
        direction = 1.0 if value > 0 else -1.0
        turn_rate = TURN_RATE_AT_FULL_SPEED * DRIVE_SPEED_MMPS / FULL_SPEED_MMPS
        duration = abs(value) / turn_rate
        client.drive_wheels(
            -direction * DRIVE_SPEED_MMPS, direction * DRIVE_SPEED_MMPS, duration
        )

    def _speak(self, client: _Client, text: str) -> None:
        with tempfile.TemporaryDirectory(prefix="cozmo-tr-") as directory:
            output = Path(directory) / "speech.wav"
            self._tts.synthesize(text, output)
            client.play_audio(str(output))


def _required_value(action: RobotAction) -> float:
    if action.value is None:
        raise RobotUnavailable("Güvenli eylemde hareket değeri eksik")
    return action.value


def _load_client_factory() -> ClientFactory:
    module = import_module("pycozmo")
    factory: object = module.Client
    if not callable(factory):
        raise RobotUnavailable("PyCozmo Client bulunamadı")
    return cast(ClientFactory, factory)


def _load_packet_factory() -> PacketFactory:
    module = import_module("pycozmo.protocol_encoder")
    factory: object = module.EnableStopOnCliff
    if not callable(factory):
        raise RobotUnavailable("Uçurum koruma paketi bulunamadı")
    constructor = cast(Callable[..., object], factory)
    return lambda enabled: constructor(enable=enabled)


def _run_shutdown(client: _Client) -> list[Exception]:
    errors: list[Exception] = []
    for operation in (client.stop_all_motors, client.disconnect, client.stop):
        try:
            operation()
        except Exception as error:
            errors.append(error)
    return errors
