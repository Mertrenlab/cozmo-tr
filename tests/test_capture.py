"""Tests for explicit, one-frame camera capture and cleanup."""

import tempfile
import unittest
from pathlib import Path

from cozmo_tr.capture import CaptureUnavailable, capture_photo


class FakeImage:
    """Write a marker instead of an actual JPEG."""

    def save(self, path: Path) -> None:
        path.write_bytes(b"image")


class FakeCameraClient:
    """Dispatch one optional camera image when streaming starts."""

    def __init__(self, image: FakeImage | None) -> None:
        self.image = image
        self.callback: object | None = None
        self.calls: list[tuple[object, ...]] = []

    def add_handler(self, event: object, callback: object, one_shot: bool) -> object:
        self.calls.append(("add", event, one_shot))
        self.callback = callback
        return "handler"

    def del_handler(self, event: object, handler: object) -> None:
        self.calls.append(("delete", event, handler))

    def enable_camera(self, enable: bool, color: bool = False) -> None:
        self.calls.append(("camera", enable, color))
        if enable and self.image is not None and callable(self.callback):
            self.callback(self, self.image)


class CameraCaptureTests(unittest.TestCase):
    """Store one requested image and always stop the camera stream."""

    def test_captures_one_photo_and_stops_stream(self) -> None:
        client = FakeCameraClient(FakeImage())
        with tempfile.TemporaryDirectory() as directory:
            path = capture_photo(
                client,
                output_dir=Path(directory),
                event_type="image-event",
                filename="photo.jpg",
                timeout=0.0,
            )
            self.assertEqual(path.read_bytes(), b"image")
        self.assertEqual(client.calls[-1], ("camera", False, False))

    def test_timeout_stops_stream_and_removes_handler(self) -> None:
        client = FakeCameraClient(None)
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaises(CaptureUnavailable),
        ):
            capture_photo(
                client,
                output_dir=Path(directory),
                event_type="image-event",
                timeout=0.0,
            )
        self.assertIn(("delete", "image-event", "handler"), client.calls)
        self.assertEqual(client.calls[-1], ("camera", False, False))


if __name__ == "__main__":
    unittest.main()
