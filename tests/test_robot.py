"""Tests for PyCozmo adaptation through an in-memory client."""

import unittest
from pathlib import Path

from cozmo_tr.actions import ActionKind, RobotAction
from cozmo_tr.robot import (
    PyCozmoRobot,
    RobotUnavailable,
    _load_client_factory,
    _load_packet_factory,
)
from cozmo_tr.tts import WavSpec


class FakeConnection:
    """Collect packets that would be sent over UDP."""

    def __init__(self) -> None:
        self.packets: list[object] = []

    def send(self, packet: object) -> None:
        self.packets.append(packet)


class FakeClient:
    """Expose the small PyCozmo surface used by the adapter."""

    def __init__(self) -> None:
        self.conn = FakeConnection()
        self.calls: list[tuple[object, ...]] = []

    def start(self) -> None:
        self.calls.append(("start",))

    def connect(self) -> None:
        self.calls.append(("connect",))

    def wait_for_robot(self, timeout: float = 5.0) -> None:
        self.calls.append(("wait", timeout))

    def drive_wheels(self, left: float, right: float, duration: float) -> None:
        self.calls.append(("drive", left, right, duration))

    def stop_all_motors(self) -> None:
        self.calls.append(("stop_motors",))

    def play_audio(self, path: str) -> None:
        self.calls.append(("audio", Path(path).suffix))

    def disconnect(self) -> None:
        self.calls.append(("disconnect",))

    def stop(self) -> None:
        self.calls.append(("stop_client",))


class FakeTts:
    """Create a placeholder file for the speaker adapter."""

    def synthesize(self, text: str, output: Path) -> WavSpec:
        output.write_bytes(text.encode("utf-8"))
        return WavSpec(22_050, 1, 2)


class RobotAdapterTests(unittest.TestCase):
    """Verify connection safety and bounded action mapping."""

    def setUp(self) -> None:
        self.client = FakeClient()
        self.robot = PyCozmoRobot(
            client_factory=lambda: self.client,
            cliff_packet_factory=lambda enabled: ("cliff", enabled),
            tts=FakeTts(),
        )

    def test_requires_connection(self) -> None:
        with self.assertRaises(RobotUnavailable):
            self.robot.execute(RobotAction(ActionKind.STOP))

    def test_connect_enables_cliff_stop(self) -> None:
        self.robot.connect()
        expected = [("start",), ("connect",), ("wait", 8.0)]
        self.assertEqual(self.client.calls[:3], expected)
        self.assertEqual(self.client.conn.packets, [("cliff", True)])

    def test_maps_move_turn_stop_and_speech(self) -> None:
        self.robot.connect()
        self.robot.execute(RobotAction(ActionKind.MOVE, value=75.0))
        self.robot.execute(RobotAction(ActionKind.TURN, value=-45.0))
        self.robot.execute(RobotAction(ActionKind.STOP))
        self.robot.execute(RobotAction(ActionKind.SPEAK, text="Merhaba"))
        names = [call[0] for call in self.client.calls]
        self.assertEqual(names.count("drive"), 2)
        self.assertIn("stop_motors", names)
        self.assertIn(("audio", ".wav"), self.client.calls)

    def test_close_stops_and_disconnects(self) -> None:
        self.robot.connect()
        self.robot.close()
        expected = [("stop_motors",), ("disconnect",), ("stop_client",)]
        self.assertEqual(self.client.calls[-3:], expected)

    def test_close_without_connection_is_safe(self) -> None:
        self.robot.close()
        self.assertEqual(self.client.calls, [])

    def test_missing_numeric_value_is_rejected(self) -> None:
        self.robot.connect()
        with self.assertRaises(RobotUnavailable):
            self.robot.execute(RobotAction(ActionKind.MOVE))

    def test_default_pycozmo_factories_load(self) -> None:
        self.assertTrue(callable(_load_client_factory()))
        self.assertTrue(callable(_load_packet_factory()))


if __name__ == "__main__":
    unittest.main()
