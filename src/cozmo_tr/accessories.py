"""Bounded direct control for Cozmo cubes and charging platform LEDs."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from time import monotonic, sleep
from typing import Protocol

from cozmo_tr.actions import ActionKind, RobotAction, SafetyPolicy
from cozmo_tr.effects import EffectClient
from cozmo_tr.errors import RobotUnavailable

DISCOVERY_TIMEOUT_SECONDS = 1.5
DISCOVERY_POLL_SECONDS = 0.05
TYPE_NAMES = {
    "cube": frozenset({"Block_LIGHTCUBE1", "Block_LIGHTCUBE2", "Block_LIGHTCUBE3"}),
    "charger": frozenset({"Charger_Basic"}),
}
LABELS = {"cube": "Küp", "charger": "Şarj istasyonu"}


class NamedType(Protocol):
    name: str


class ObjectRecord(Protocol):
    object_type: NamedType


class AccessoryConnection(Protocol):
    """Describe the low-level object packet connection surface."""

    def send(self, packet: object) -> None: ...
    def wait_for(self, event: object, timeout: float | None = None) -> None: ...


class ObjectClient(Protocol):
    """Expose discovered and connected object snapshots."""

    conn: AccessoryConnection
    available_objects: Mapping[int, ObjectRecord]
    connected_objects: Mapping[int, Mapping[str, object]]


class AccessoryClient(EffectClient, ObjectClient, Protocol):
    """Combine object and speech surfaces for user feedback."""


Packet2 = Callable[[int, bool], object]
Packet1 = Callable[[int], object]
LightPacket = Callable[[tuple[object, ...]], object]


@dataclass(frozen=True, slots=True)
class AccessoryProtocol:
    """Hold injectable PyCozmo packet and light constructors."""

    connect: Packet2
    connection_event: object
    select: Packet1
    illuminate: LightPacket
    lights: Mapping[str, object]


class AccessoryEffects(Protocol):
    def execute(self, client: EffectClient, action: RobotAction) -> None: ...


class AccessoryController:
    """Discover, connect, and illuminate one accessory with finite waits."""

    def __init__(
        self,
        protocol: AccessoryProtocol | None = None,
        timeout: float = DISCOVERY_TIMEOUT_SECONDS,
        clock: Callable[[], float] = monotonic,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        self._protocol = protocol or load_accessory_protocol()
        self._timeout = max(0.0, timeout)
        self._clock = clock
        self._sleep = sleeper

    def count(self, client: ObjectClient, target: str) -> int:
        """Return the advertised object count after one bounded scan window."""
        self._wait_for_factory(client, target)
        return len(self._matching_factories(client, target))

    def set_lights(self, client: ObjectClient, target: str, color: str) -> None:
        """Connect to the first matching object and set its finite LED state."""
        light = self._protocol.lights.get(color)
        if light is None:
            raise RobotUnavailable("Aksesuar ışık rengi desteklenmiyor")
        factory_id = self._wait_for_factory(client, target)
        if factory_id is None:
            raise RobotUnavailable(f"{self._label(target)} bulunamadı")
        object_id = self._object_id(client, factory_id)
        if object_id is None:
            object_id = self._connect(client, factory_id, target)
        self._illuminate(client, object_id, target, light)

    def _connect(self, client: ObjectClient, factory_id: int, target: str) -> int:
        client.conn.send(self._protocol.connect(factory_id, True))
        try:
            client.conn.wait_for(self._protocol.connection_event, self._timeout)
        except Exception as error:
            raise RobotUnavailable(f"{self._label(target)} bağlanamadı") from error
        object_id = self._object_id(client, factory_id)
        if object_id is None:
            raise RobotUnavailable(f"{self._label(target)} bağlanamadı")
        return object_id

    def _illuminate(
        self, client: ObjectClient, object_id: int, target: str, light: object
    ) -> None:
        off = self._protocol.lights["off"]
        states = (light,) * 4 if target == "cube" else (light, light, light, off)
        client.conn.send(self._protocol.select(object_id))
        client.conn.send(self._protocol.illuminate(states))

    def _wait_for_factory(self, client: ObjectClient, target: str) -> int | None:
        deadline = self._clock() + self._timeout
        while True:
            matches = self._matching_factories(client, target)
            if matches:
                return matches[0]
            remaining = deadline - self._clock()
            if remaining <= 0:
                return None
            self._sleep(min(DISCOVERY_POLL_SECONDS, remaining))

    @staticmethod
    def _object_id(client: ObjectClient, factory_id: int) -> int | None:
        for object_id, record in client.connected_objects.items():
            if record.get("factory_id") == factory_id:
                return object_id
        return None

    @staticmethod
    def _matching_factories(client: ObjectClient, target: str) -> list[int]:
        names = TYPE_NAMES.get(target)
        if names is None:
            raise RobotUnavailable("Aksesuar türü desteklenmiyor")
        return sorted(
            factory_id
            for factory_id, record in client.available_objects.items()
            if record.object_type.name in names
        )

    @staticmethod
    def _label(target: str) -> str:
        return LABELS.get(target, "Aksesuar")


class AccessorySession:
    """Translate one safe named command into object control or speech."""

    def __init__(
        self, effects: AccessoryEffects, controller: AccessoryController | None = None
    ) -> None:
        self._effects = effects
        self._controller = controller or AccessoryController()
        self._policy = SafetyPolicy()

    def play(self, client: AccessoryClient, command: str) -> None:
        """Execute one already-safe accessory command."""
        target, operation = _split_command(command)
        if operation == "count":
            count = self._controller.count(client, target)
            action = RobotAction(ActionKind.SPEAK, text=f"{count} küp görüyorum.")
            self._effects.execute(client, self._policy.enforce(action))
            return
        self._controller.set_lights(client, target, operation)


def _split_command(command: str) -> tuple[str, str]:
    parts = command.split("_", maxsplit=1)
    if len(parts) != 2 or parts[0] not in TYPE_NAMES:
        raise RobotUnavailable("Aksesuar komutu desteklenmiyor")
    return parts[0], parts[1]


def load_accessory_protocol() -> AccessoryProtocol:
    """Load PyCozmo packet constructors only on the hardware path."""
    protocol = import_module("pycozmo.protocol_encoder")
    lights = import_module("pycozmo.lights")
    return AccessoryProtocol(
        connect=lambda factory, enabled: protocol.ObjectConnect(
            factory_id=factory, connect=enabled
        ),
        connection_event=protocol.ObjectConnectionState,
        select=lambda object_id: protocol.CubeId(object_id=object_id),
        illuminate=lambda states: protocol.CubeLights(states=states),
        lights={name: getattr(lights, f"{name}_light") for name in (*COLORS, "off")},
    )


COLORS = ("red", "green", "blue", "white")
