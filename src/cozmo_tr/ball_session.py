"""Run one bounded ball interaction using Cozmo's camera.

Responsible for: one frame, detection, safety validation, and primitive effects.
Not responsible for: continuous tracking, learning, or direct motor calls.
"""

from collections.abc import Callable
from typing import Protocol

from cozmo_tr.actions import ActionKind, RobotAction, SafetyPolicy
from cozmo_tr.ball import RgbFrame, detect_red_ball, plan_ball_motion
from cozmo_tr.capture import CameraClient, CaptureUnavailable, capture_frame
from cozmo_tr.effects import EffectClient
from cozmo_tr.errors import RobotUnavailable


class PrimitiveExecutor(Protocol):
    """Execute only actions already validated by a safety policy."""

    def execute(self, client: EffectClient, action: RobotAction) -> None: ...


class ActionPolicy(Protocol):
    """Validate one planned primitive before execution."""

    def enforce(self, action: RobotAction) -> RobotAction: ...


FrameCapture = Callable[[CameraClient], RgbFrame]


class BallSession:
    """Convert one camera frame into a finite safe robot plan."""

    def __init__(
        self,
        executor: PrimitiveExecutor,
        capture: FrameCapture = capture_frame,
        policy: ActionPolicy | None = None,
    ) -> None:
        self._executor = executor
        self._capture = capture
        self._policy = policy or SafetyPolicy()

    def play(self, client: EffectClient, mode: str) -> None:
        """Run one frame and stop; raise an actionable error on camera failure."""
        try:
            observation = detect_red_ball(self._capture(client))
        except CaptureUnavailable as error:
            raise RobotUnavailable("Top kamerasından görüntü alınamadı") from error
        plan = plan_ball_motion(observation, mode)
        if observation is None:
            plan += (RobotAction(ActionKind.SPEAK, text="Topu göremedim."),)
        for action in plan:
            safe = self._policy.enforce(action)
            self._executor.execute(client, safe)
