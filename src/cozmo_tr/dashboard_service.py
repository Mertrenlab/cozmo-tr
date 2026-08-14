"""Serialize dashboard access to robot, safety, and local microphone ports.

Responsible for: explicit connection state and one-at-a-time safe turns.
Not responsible for: HTTP, HTML, authentication tokens, or robot effects.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Protocol

from cozmo_tr.actions import RobotAction
from cozmo_tr.orchestrator import TurnResult, TurnService
from cozmo_tr.robot import PyCozmoRobot
from cozmo_tr.stt import VoskTranscriber

DEFAULT_MODEL = Path("models/vosk-model-small-tr-0.3")


class ManagedRobot(Protocol):
    """Expose the robot lifecycle required by one dashboard session."""

    def connect(self) -> None: ...
    def execute(self, action: RobotAction) -> None: ...
    def close(self) -> None: ...


class Transcriber(Protocol):
    """Expose one bounded local microphone capture."""

    def transcribe_once(self, seconds: float) -> str: ...


RobotFactory = Callable[[], ManagedRobot]
TranscriberFactory = Callable[[], Transcriber]


class DashboardError(RuntimeError):
    """Report a safe user-facing dashboard failure with an HTTP status."""

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True, slots=True)
class DashboardTurn:
    """Pair microphone text with the resulting safe command turn."""

    transcript: str
    result: TurnResult


class DashboardService:
    """Own one explicit PyCozmo session and serialize every command."""

    def __init__(
        self,
        robot_factory: RobotFactory = PyCozmoRobot,
        transcriber_factory: TranscriberFactory | None = None,
    ) -> None:
        self._robot_factory = robot_factory
        self._transcriber_factory = transcriber_factory or _default_transcriber
        self._robot: ManagedRobot | None = None
        self._lock = Lock()

    @property
    def connected(self) -> bool:
        """Return a synchronized snapshot of explicit connection state."""
        with self._lock:
            return self._robot is not None

    def connect(self) -> None:
        """Connect once; leave no partial dashboard state on failure."""
        with self._lock:
            if self._robot is not None:
                return
            robot = self._robot_factory()
            robot.connect()
            self._robot = robot

    def execute(self, text: str) -> TurnResult:
        """Run one typed command through the existing parser and safety policy."""
        with self._lock:
            robot = self._require_robot()
            return TurnService(robot).handle(text)

    def listen(self, seconds: float) -> DashboardTurn:
        """Capture one local microphone window and execute its safe transcript."""
        with self._lock:
            robot = self._require_robot()
            transcript = self._transcriber_factory().transcribe_once(seconds)
            result = TurnService(robot).handle(transcript)
            return DashboardTurn(transcript, result)

    def disconnect(self) -> None:
        """Clear state before closing so a failed close cannot look connected."""
        with self._lock:
            robot = self._robot
            self._robot = None
        if robot is not None:
            robot.close()

    def close(self) -> None:
        """Support server shutdown using the same idempotent disconnect path."""
        self.disconnect()

    def _require_robot(self) -> ManagedRobot:
        if self._robot is None:
            raise DashboardError("Önce Cozmo'ya bağlanın.", 409)
        return self._robot


def _default_transcriber() -> Transcriber:
    return VoskTranscriber(DEFAULT_MODEL)
