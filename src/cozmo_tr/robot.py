"""Manage the direct PyCozmo connection lifecycle.

Responsible for: connection, cliff stop, effect delegation, and shutdown.
Not responsible for: effect details, parsing, safety decisions, or STT.
"""

from collections.abc import Callable
from importlib import import_module
from typing import Protocol, cast

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.ball_session import BallSession
from cozmo_tr.effects import EffectClient, RobotEffects, SpeechSynthesizer
from cozmo_tr.errors import RobotUnavailable as RobotUnavailable

CONNECT_TIMEOUT_SECONDS = 8.0


class _Connection(Protocol):
    def send(self, packet: object) -> None:
        """Send one encoded protocol packet."""
        ...


class _Client(EffectClient, Protocol):
    conn: _Connection

    def start(self) -> None: ...
    def connect(self) -> None: ...
    def wait_for_robot(self, timeout: float = 5.0) -> None: ...
    def disconnect(self) -> None: ...
    def stop(self) -> None: ...


class _Effects(Protocol):
    def execute(self, client: EffectClient, action: RobotAction) -> None: ...


class _BallSession(Protocol):
    def play(self, client: EffectClient, mode: str) -> None: ...


ClientFactory = Callable[[], _Client]
PacketFactory = Callable[[bool], object]


class PyCozmoRobot:
    """Manage one direct-Wi-Fi PyCozmo client behind the robot port."""

    def __init__(
        self,
        client_factory: ClientFactory | None = None,
        cliff_packet_factory: PacketFactory | None = None,
        tts: SpeechSynthesizer | None = None,
        effects: _Effects | None = None,
        ball_session: _BallSession | None = None,
    ) -> None:
        """Store injectable factories; no connection occurs yet."""
        self._client_factory = client_factory
        self._packet_factory = cliff_packet_factory
        self._effects = effects or RobotEffects(tts=tts)
        self._ball_session = ball_session or BallSession(self._effects)
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
        if action.kind is ActionKind.BALL:
            self._ball_session.play(client, action.text)
            return
        self._effects.execute(client, action)

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
