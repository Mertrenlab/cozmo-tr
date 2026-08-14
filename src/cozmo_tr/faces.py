"""Generate small local expressions for Cozmo's OLED face.

Responsible for: deterministic 128x64 monochrome face images.
Not responsible for: display transport, animation assets, or recognition.
"""

from collections.abc import Callable
from importlib import import_module
from typing import Protocol, cast

FACE_WIDTH = 128
FACE_HEIGHT = 64
EYE_TOP = 16
EYE_BOTTOM = 42
LEFT_EYE = (22, EYE_TOP, 50, EYE_BOTTOM)
RIGHT_EYE = (78, EYE_TOP, 106, EYE_BOTTOM)
WHITE = 1
BLACK = 0

Box = tuple[int, int, int, int]


class FaceImage(Protocol):
    """Expose the image metadata used by PyCozmo and tests."""

    size: tuple[int, int]
    mode: str


class Drawer(Protocol):
    """Describe only the Pillow drawing operations used by expressions."""

    def rounded_rectangle(self, box: Box, radius: int, fill: int) -> None: ...
    def arc(self, box: Box, start: int, end: int, fill: int, width: int) -> None: ...
    def ellipse(self, box: Box, outline: int, width: int) -> None: ...
    def polygon(self, points: tuple[tuple[int, int], ...], fill: int) -> None: ...


ImageFactory = Callable[[str, tuple[int, int], int], FaceImage]
DrawFactory = Callable[[FaceImage], Drawer]
FaceDraw = Callable[[Drawer], None]


def render_face(name: str) -> FaceImage:
    """Return one supported OLED image; raise ValueError for unknown names."""
    renderers: dict[str, FaceDraw] = {
        "happy": _happy,
        "sad": _sad,
        "surprised": _surprised,
        "angry": _angry,
        "neutral": _neutral,
    }
    renderer = renderers.get(name)
    if renderer is None:
        raise ValueError(f"Bilinmeyen yüz ifadesi: {name}")
    image_factory, draw_factory = _load_pillow()
    image = image_factory("1", (FACE_WIDTH, FACE_HEIGHT), BLACK)
    renderer(draw_factory(image))
    return image


def _load_pillow() -> tuple[ImageFactory, DrawFactory]:
    image_new: object = import_module("PIL.Image").new
    image_draw: object = import_module("PIL.ImageDraw").Draw
    if not callable(image_new) or not callable(image_draw):
        raise RuntimeError("Pillow görüntü API'si bulunamadı")
    return cast(ImageFactory, image_new), cast(DrawFactory, image_draw)


def _neutral(draw: Drawer) -> None:
    draw.rounded_rectangle(LEFT_EYE, radius=7, fill=WHITE)
    draw.rounded_rectangle(RIGHT_EYE, radius=7, fill=WHITE)


def _happy(draw: Drawer) -> None:
    draw.arc(LEFT_EYE, start=180, end=360, fill=WHITE, width=5)
    draw.arc(RIGHT_EYE, start=180, end=360, fill=WHITE, width=5)
    draw.arc((48, 34, 80, 58), start=0, end=180, fill=WHITE, width=3)


def _sad(draw: Drawer) -> None:
    draw.arc(LEFT_EYE, start=0, end=180, fill=WHITE, width=5)
    draw.arc(RIGHT_EYE, start=0, end=180, fill=WHITE, width=5)
    draw.arc((48, 44, 80, 62), start=180, end=360, fill=WHITE, width=3)


def _surprised(draw: Drawer) -> None:
    draw.ellipse(LEFT_EYE, outline=WHITE, width=5)
    draw.ellipse(RIGHT_EYE, outline=WHITE, width=5)
    draw.ellipse((58, 45, 70, 59), outline=WHITE, width=2)


def _angry(draw: Drawer) -> None:
    draw.polygon(((22, 24), (50, 16), (50, 42), (26, 40)), fill=WHITE)
    draw.polygon(((78, 16), (106, 24), (102, 40), (78, 42)), fill=WHITE)
