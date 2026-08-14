"""Detect a red ball and plan one bounded direct-control response.

Responsible for: pure pixel classification and finite RobotAction plans.
Not responsible for: camera streaming, repeated tracking, or motor I/O.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from cozmo_tr.actions import ActionKind, RobotAction

Pixel = tuple[int, int, int]
Point = tuple[int, int]
MIN_RED_VALUE = 140
RED_DOMINANCE = 1.5
MIN_TARGET_PIXELS = 20
MIN_ASPECT_RATIO = 0.65
MAX_ASPECT_RATIO = 1.35
MIN_FILL_RATIO = 0.35
MIN_CONFIDENCE = 0.5
TURN_THRESHOLD = 0.2
FAR_AREA_FRACTION = 0.04
NEAR_AREA_FRACTION = 0.16
TURN_STEP_DEGREES = 15.0
APPROACH_DISTANCE_MM = 40.0
PLAY_DISTANCE_MM = 30.0
RETREAT_DISTANCE_MM = -30.0


class RgbFrame(Protocol):
    """Describe the Pillow-compatible frame surface used by detection."""

    size: tuple[int, int]

    def convert(self, mode: str) -> "RgbFrame": ...
    def getdata(self) -> Iterable[Pixel]: ...


@dataclass(frozen=True, slots=True)
class BallObservation:
    """Describe horizontal target position, relative size, and confidence."""

    offset_x: float
    area_fraction: float
    confidence: float


def detect_red_ball(frame: RgbFrame) -> BallObservation | None:
    """Return one geometric red-target observation or None without guessing."""
    width, height = frame.size
    points = _red_points(frame.convert("RGB").getdata(), width)
    if len(points) < MIN_TARGET_PIXELS:
        return None
    return _observation(points, width, height)


def plan_ball_motion(
    observation: BallObservation | None, mode: str
) -> tuple[RobotAction, ...]:
    """Return a finite safe-candidate plan; never call motors directly."""
    if mode not in {"find", "play"}:
        raise ValueError(f"Bilinmeyen top modu: {mode}")
    if observation is None or observation.confidence < MIN_CONFIDENCE:
        return _stop()
    if observation.offset_x < -TURN_THRESHOLD:
        return _with_stop(RobotAction(ActionKind.TURN, TURN_STEP_DEGREES))
    if observation.offset_x > TURN_THRESHOLD:
        return _with_stop(RobotAction(ActionKind.TURN, -TURN_STEP_DEGREES))
    return _centered_plan(observation.area_fraction, mode)


def _red_points(pixels: Iterable[Pixel], width: int) -> list[Point]:
    return [
        (index % width, index // width)
        for index, pixel in enumerate(pixels)
        if _is_red(pixel)
    ]


def _is_red(pixel: Pixel) -> bool:
    red, green, blue = pixel
    return (
        red >= MIN_RED_VALUE
        and red >= green * RED_DOMINANCE
        and red >= blue * RED_DOMINANCE
    )


def _observation(
    points: list[Point], width: int, height: int
) -> BallObservation | None:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    box_width = max(xs) - min(xs) + 1
    box_height = max(ys) - min(ys) + 1
    aspect = box_width / box_height
    fill = len(points) / (box_width * box_height)
    if not MIN_ASPECT_RATIO <= aspect <= MAX_ASPECT_RATIO or fill < MIN_FILL_RATIO:
        return None
    center_x = sum(xs) / len(xs)
    offset = (2.0 * center_x / max(1, width - 1)) - 1.0
    area = len(points) / (width * height)
    confidence = min(1.0, len(points) / (MIN_TARGET_PIXELS * 2.0))
    return BallObservation(offset, area, confidence)


def _centered_plan(area: float, mode: str) -> tuple[RobotAction, ...]:
    if area > NEAR_AREA_FRACTION:
        return _with_stop(RobotAction(ActionKind.MOVE, RETREAT_DISTANCE_MM))
    if mode == "play":
        return (
            RobotAction(ActionKind.MOVE, PLAY_DISTANCE_MM),
            RobotAction(ActionKind.MOVE, -PLAY_DISTANCE_MM),
            RobotAction(ActionKind.STOP),
        )
    if area < FAR_AREA_FRACTION:
        return _with_stop(RobotAction(ActionKind.MOVE, APPROACH_DISTANCE_MM))
    return _stop()


def _with_stop(action: RobotAction) -> tuple[RobotAction, ...]:
    return action, RobotAction(ActionKind.STOP)


def _stop() -> tuple[RobotAction, ...]:
    return (RobotAction(ActionKind.STOP),)
