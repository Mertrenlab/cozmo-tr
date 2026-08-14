"""Tests for bounded direct cube and charger control."""

import unittest
from dataclasses import dataclass

from cozmo_tr.accessories import AccessoryController, AccessoryProtocol

from cozmo_tr.errors import RobotUnavailable


@dataclass(frozen=True)
class FakeObject:
    """Expose the object type name discovered by PyCozmo."""

    object_type: object


class NamedType:
    """Behave like PyCozmo's ObjectType enum for clean-room tests."""

    def __init__(self, name: str) -> None:
        self.name = name


class FakeConnection:
    """Collect protocol packets and optionally materialize a connection."""

    def __init__(self) -> None:
        self.packets: list[object] = []
        self.waits: list[tuple[object, float | None]] = []

    def send(self, packet: object) -> None:
        self.packets.append(packet)

    def wait_for(self, event: object, timeout: float | None = None) -> None:
        self.waits.append((event, timeout))


class FakeClient:
    """Expose only PyCozmo's object discovery dictionaries."""

    def __init__(self) -> None:
        self.conn = FakeConnection()
        self.available_objects: dict[int, FakeObject] = {}
        self.connected_objects: dict[int, dict[str, object]] = {}


def protocol() -> AccessoryProtocol:
    """Create inspectable packet factories and light values."""
    return AccessoryProtocol(
        connect=lambda factory_id, enabled: ("connect", factory_id, enabled),
        connection_event="connection-event",
        select=lambda object_id: ("select", object_id),
        illuminate=lambda states: ("lights", states),
        lights={"red": "RED", "blue": "BLUE", "off": "OFF"},
    )


class AccessoryControllerTests(unittest.TestCase):
    """Control advertised objects without infinite discovery loops."""

    def setUp(self) -> None:
        self.client = FakeClient()
        self.controller = AccessoryController(
            protocol=protocol(), timeout=0.0, sleeper=lambda _seconds: None
        )

    def test_counts_every_light_cube_variant(self) -> None:
        self.client.available_objects = {
            10: FakeObject(NamedType("Block_LIGHTCUBE1")),
            20: FakeObject(NamedType("Block_LIGHTCUBE2")),
            30: FakeObject(NamedType("Block_LIGHTCUBE3")),
            40: FakeObject(NamedType("Charger_Basic")),
        }
        self.assertEqual(self.controller.count(self.client, "cube"), 3)
        self.assertEqual(self.controller.count(self.client, "charger"), 1)

    def test_reuses_connected_cube_and_sets_all_four_leds(self) -> None:
        self.client.available_objects[20] = FakeObject(NamedType("Block_LIGHTCUBE2"))
        self.client.connected_objects[7] = {"factory_id": 20}
        self.controller.set_lights(self.client, "cube", "red")
        self.assertEqual(
            self.client.conn.packets,
            [("select", 7), ("lights", ("RED",) * 4)],
        )
        self.assertEqual(self.client.conn.waits, [])

    def test_connects_matching_factory_with_bounded_wait(self) -> None:
        self.client.available_objects[30] = FakeObject(NamedType("Block_LIGHTCUBE3"))
        original_wait = self.client.conn.wait_for

        def connect_during_wait(event: object, timeout: float | None = None) -> None:
            self.client.connected_objects[9] = {"factory_id": 30}
            original_wait(event, timeout)

        self.client.conn.wait_for = connect_during_wait
        self.controller.set_lights(self.client, "cube", "blue")
        self.assertEqual(self.client.conn.packets[0], ("connect", 30, True))
        self.assertEqual(self.client.conn.waits, [("connection-event", 0.0)])
        self.assertEqual(self.client.conn.packets[-1], ("lights", ("BLUE",) * 4))

    def test_charger_uses_three_leds_and_keeps_fourth_off(self) -> None:
        self.client.available_objects[40] = FakeObject(NamedType("Charger_Basic"))
        self.client.connected_objects[11] = {"factory_id": 40}
        self.controller.set_lights(self.client, "charger", "red")
        expected = ("lights", ("RED", "RED", "RED", "OFF"))
        self.assertEqual(self.client.conn.packets[-1], expected)

    def test_missing_or_unconfirmed_object_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(RobotUnavailable, "Küp bulunamadı"):
            self.controller.set_lights(self.client, "cube", "red")
        self.client.available_objects[40] = FakeObject(NamedType("Charger_Basic"))
        with self.assertRaisesRegex(RobotUnavailable, "bağlanamadı"):
            self.controller.set_lights(self.client, "charger", "red")


if __name__ == "__main__":
    unittest.main()
