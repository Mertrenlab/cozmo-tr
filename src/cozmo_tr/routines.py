"""Expand named routines into bounded primitive robot actions.

Responsible for: deterministic, finite gesture plans.
Not responsible for: safety validation, timing, or hardware calls.
"""

from cozmo_tr.actions import ActionKind, RobotAction

ROUTINES: dict[str, tuple[RobotAction, ...]] = {
    "greet": (
        RobotAction(ActionKind.HEAD, 25.0),
        RobotAction(ActionKind.LIFT, 70.0),
        RobotAction(ActionKind.SPEAK, text="Selam!"),
        RobotAction(ActionKind.STOP),
    ),
    "nod": (
        RobotAction(ActionKind.HEAD, 30.0),
        RobotAction(ActionKind.HEAD, -10.0),
        RobotAction(ActionKind.HEAD, 20.0),
        RobotAction(ActionKind.STOP),
    ),
    "dance": (
        RobotAction(ActionKind.TURN, 35.0),
        RobotAction(ActionKind.TURN, -70.0),
        RobotAction(ActionKind.TURN, 35.0),
        RobotAction(ActionKind.LIFT, 92.0),
        RobotAction(ActionKind.LIFT, 32.0),
        RobotAction(ActionKind.HEAD, 30.0),
        RobotAction(ActionKind.HEAD, 5.0),
        RobotAction(ActionKind.STOP),
    ),
    "goodbye": (
        RobotAction(ActionKind.SPEAK, text="Görüşürüz!"),
        RobotAction(ActionKind.HEAD, -15.0),
        RobotAction(ActionKind.LIFT, 32.0),
        RobotAction(ActionKind.STOP),
    ),
}


def expand_action(action: RobotAction) -> tuple[RobotAction, ...]:
    """Return one primitive or a finite known routine; perform no I/O."""
    if action.kind is not ActionKind.ROUTINE:
        return (action,)
    return ROUTINES[action.text]
