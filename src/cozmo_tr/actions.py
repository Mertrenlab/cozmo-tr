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
        if action.kind is ActionKind.MOVE:
            return self._safe_numeric(action, self._limits.max_distance_mm)
        if action.kind is ActionKind.TURN:
            return self._safe_numeric(action, self._limits.max_turn_degrees)
        raise UnsafeAction("Desteklenmeyen robot eylemi")

    def _safe_speech(self, action: RobotAction) -> RobotAction:
        text = action.text.strip()
        if not text:
            raise UnsafeAction("Konuşma metni boş olamaz")
        return replace(action, text=text[: self._limits.max_speech_chars])

    @staticmethod
    def _safe_numeric(action: RobotAction, limit: float) -> RobotAction:
        value = action.value
        if value is None or not isfinite(value) or value == 0:
            raise UnsafeAction("Hareket değeri sıfırdan farklı ve sonlu olmalı")
        bounded = max(-limit, min(limit, value))
        return replace(action, value=bounded)
