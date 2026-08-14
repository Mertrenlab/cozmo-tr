"""Coordinate one user command through parsing, safety, and robot I/O.

Responsible for: sequencing one deterministic interaction turn.
Not responsible for: CLI presentation, STT, TTS conversion, or motor details.
"""

from dataclasses import dataclass
from typing import Protocol

from cozmo_tr.actions import RobotAction, SafetyPolicy, UnsafeAction
from cozmo_tr.commands import parse_command


class RobotPort(Protocol):
    """Accept only actions that already passed the safety policy."""

    def execute(self, action: RobotAction) -> None:
        """Perform one bounded action or raise an adapter-specific error."""
        ...


@dataclass(frozen=True, slots=True)
class TurnResult:
    """Describe whether a user turn reached the robot boundary."""

    accepted: bool
    message: str
    action: RobotAction | None = None


class TurnService:
    """Run parser and safety checks before invoking a robot port."""

    def __init__(self, robot: RobotPort, policy: SafetyPolicy | None = None) -> None:
        """Bind a robot port and optional safety policy for later turns."""
        self._robot = robot
        self._policy = policy or SafetyPolicy()

    def handle(self, text: str) -> TurnResult:
        """Execute one understood safe command; reject all other text."""
        action = parse_command(text)
        if action is None:
            return TurnResult(False, _unknown_message())
        try:
            safe = self._policy.enforce(action)
        except UnsafeAction as error:
            return TurnResult(False, f"Komut güvenli değil: {error}")
        self._robot.execute(safe)
        return TurnResult(True, "Komut güvenle uygulandı.", safe)


def _unknown_message() -> str:
    return "Anlayamadım. Örnek: ileri 50, geri 50, sola 30, sağa 30 veya dur."
