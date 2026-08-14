"""Capture one explicit Cozmo camera frame to local storage.

Responsible for: bounded camera streaming, one file, and handler cleanup.
Not responsible for: recognition, continuous recording, or cloud upload.
"""

from collections.abc import Callable
from datetime import datetime
from importlib import import_module
from pathlib import Path
from threading import Event
from typing import Protocol

from cozmo_tr.ball import RgbFrame

DEFAULT_CAPTURE_DIR = Path("captures")
CAPTURE_TIMEOUT_SECONDS = 3.0


class CaptureUnavailable(RuntimeError):
    """Report a camera timeout, storage error, or unavailable event API."""


class CameraImage(RgbFrame, Protocol):
    """Describe the image save surface returned by PyCozmo."""

    def save(self, path: Path) -> None: ...


ImageCallback = Callable[[object, CameraImage], None]


class CameraClient(Protocol):
    """Describe the public PyCozmo camera event surface."""

    def add_handler(
        self, event: object, callback: ImageCallback, one_shot: bool
    ) -> object: ...

    def del_handler(self, event: object, handler: object) -> None: ...
    def enable_camera(self, enable: bool, color: bool = False) -> None: ...


def capture_photo(
    client: CameraClient,
    output_dir: Path = DEFAULT_CAPTURE_DIR,
    event_type: object | None = None,
    filename: str | None = None,
    timeout: float = CAPTURE_TIMEOUT_SECONDS,
) -> Path:
    """Save one requested frame, stop streaming, or raise with no silent retry."""
    image = capture_frame(client, event_type=event_type, timeout=timeout)
    return _save_image(image, output_dir, filename)


def capture_frame(
    client: CameraClient,
    event_type: object | None = None,
    timeout: float = CAPTURE_TIMEOUT_SECONDS,
) -> CameraImage:
    """Return one requested frame and always stop camera streaming."""
    received = Event()
    images: list[CameraImage] = []

    def on_image(_client: object, image: CameraImage) -> None:
        images.append(image)
        received.set()

    event = event_type or _load_camera_event()
    handler = client.add_handler(event, on_image, one_shot=True)
    try:
        client.enable_camera(True, color=True)
        if not received.wait(timeout):
            raise CaptureUnavailable("Kamera karesi zamanında gelmedi")
        return images[0]
    finally:
        client.del_handler(event, handler)
        client.enable_camera(False)


def _save_image(image: CameraImage, output_dir: Path, filename: str | None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    name = filename or datetime.now().strftime("cozmo-%Y%m%d-%H%M%S.jpg")
    target = output_dir / name
    try:
        image.save(target)
    except OSError as error:
        raise CaptureUnavailable(f"Fotoğraf kaydedilemedi: {target}") from error
    return target


def _load_camera_event() -> object:
    module = import_module("pycozmo.event")
    return module.EvtNewRawCameraImage
