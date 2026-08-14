"""Typed robot actions and mandatory safety enforcement.

Responsible for: the narrow-waist action contract and physical bounds.
Not responsible for: Turkish parsing or robot hardware calls.
"""

from dataclasses import dataclass, replace
from enum import StrEnum
from math import isfinite


class ActionKind(StrEnum):
    """Supported action categories crossing the robot boundary."""

    STOP = "stop"
    MOVE = "move"
    TURN = "turn"
    SPEAK = "speak"
    HEAD = "head"
    LIFT = "lift"
    LIGHTS = "lights"
    HEADLIGHT = "headlight"
    FACE = "face"
    CAMERA = "camera"
    STATUS = "status"
    VOLUME = "volume"
    ROUTINE = "routine"
    BALL = "ball"


@dataclass(frozen=True, slots=True)
class RobotAction:
    """Describe one requested robot effect without performing I/O."""

    kind: ActionKind
    value: float | None = None
    text: str = ""


@dataclass(frozen=True, slots=True)
class SafetyLimits:
    """Store named physical and speech limits for one demo action."""

    max_distance_mm: float = 150.0
    max_turn_degrees: float = 90.0
    max_speech_chars: int = 160
    min_head_degrees: float = -25.0
    max_head_degrees: float = 44.5
    min_lift_mm: float = 32.0
    max_lift_mm: float = 92.0
    min_volume_percent: float = 0.0
    max_volume_percent: float = 100.0


NAMED_VALUES: dict[ActionKind, frozenset[str]] = {
    ActionKind.LIGHTS: frozenset({"off", "red", "green", "blue", "white"}),
    ActionKind.FACE: frozenset({"happy", "sad", "surprised", "angry", "neutral"}),
    ActionKind.CAMERA: frozenset({"capture"}),
    ActionKind.STATUS: frozenset({"battery"}),
    ActionKind.ROUTINE: frozenset({"dance", "greet", "nod", "goodbye"}),
    ActionKind.BALL: frozenset({"find", "play"}),
}


class UnsafeAction(ValueError):
    """Report an action that cannot be made safe without guessing."""


class SafetyPolicy:
    """Validate and bound every action before it reaches a robot port."""

    def __init__(self, limits: SafetyLimits | None = None) -> None:
        """Create a policy using explicit limits or conservative defaults."""
        self._limits = limits or SafetyLimits()

    def enforce(self, action: RobotAction) -> RobotAction:
        """Return a bounded action or raise when intent is unsafe."""
        if action.kind is ActionKind.STOP:
            return action
        if action.kind is ActionKind.SPEAK:
            return self._safe_speech(action)
        if action.kind is ActionKind.HEADLIGHT:
            return self._safe_headlight(action)
        numeric = self._numeric_range(action.kind)
        if numeric is not None:
            low, high, allow_zero = numeric
            return self._safe_numeric(action, low, high, allow_zero)
        allowed = NAMED_VALUES.get(action.kind)
        if allowed is not None:
            return self._safe_named(action, allowed)
        raise UnsafeAction("Desteklenmeyen robot eylemi")

    def _numeric_range(self, kind: ActionKind) -> tuple[float, float, bool] | None:
        ranges = {
            ActionKind.MOVE: (
                -self._limits.max_distance_mm,
                self._limits.max_distance_mm,
                False,
            ),
            ActionKind.TURN: (
                -self._limits.max_turn_degrees,
                self._limits.max_turn_degrees,
                False,
            ),
            ActionKind.HEAD: (
                self._limits.min_head_degrees,
                self._limits.max_head_degrees,
                True,
            ),
            ActionKind.LIFT: (self._limits.min_lift_mm, self._limits.max_lift_mm, True),
            ActionKind.VOLUME: (
                self._limits.min_volume_percent,
                self._limits.max_volume_percent,
                True,
            ),
        }
        return ranges.get(kind)

    def _safe_speech(self, action: RobotAction) -> RobotAction:
        text = action.text.strip()
        if not text:
            raise UnsafeAction("Konuşma metni boş olamaz")
        return replace(action, text=text[: self._limits.max_speech_chars])

    @staticmethod
    def _safe_numeric(
        action: RobotAction, low: float, high: float, allow_zero: bool
    ) -> RobotAction:
        value = action.value
        if value is None or not isfinite(value) or (value == 0 and not allow_zero):
            raise UnsafeAction("Hareket değeri sıfırdan farklı ve sonlu olmalı")
        bounded = max(low, min(high, value))
        return replace(action, value=bounded)

    @staticmethod
    def _safe_named(action: RobotAction, allowed: frozenset[str]) -> RobotAction:
        if action.text not in allowed:
            raise UnsafeAction("Eylem adı desteklenmiyor")
        return action

    @staticmethod
    def _safe_headlight(action: RobotAction) -> RobotAction:
        if action.value not in (0.0, 1.0):
            raise UnsafeAction("Kafa ışığı yalnız açık veya kapalı olabilir")
        return action
