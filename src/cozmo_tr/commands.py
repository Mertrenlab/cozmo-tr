"""Deterministic Turkish text-to-action parsing.

Responsible for: recognizing a deliberately small Turkish command grammar.
Not responsible for: fuzzy intent guessing, safety bounds, or hardware I/O.
"""

import re

from cozmo_tr.actions import ActionKind, RobotAction

DEFAULT_DISTANCE_MM = 50.0
DEFAULT_TURN_DEGREES = 45.0
ACTIVATION_RE = re.compile(r"^(?:(?:hey|ok)\s+)?(?:cozmo|cosmo|kozmo)[,\s]+", re.I)
NUMBER_RE = re.compile(r"(?<!\w)(\d+(?:[.,]\d+)?)(?!\w)")
SPEECH_RE = re.compile(r"^(?:söyle|de)\s+(.+)$", re.I)
STOP_RE = re.compile(r"\b(?:dur|stop)\b", re.I)

MOVEMENT_PATTERNS: tuple[tuple[re.Pattern[str], ActionKind, float], ...] = (
    (re.compile(r"\b(?:ileri|öne)\b", re.I), ActionKind.MOVE, 1.0),
    (re.compile(r"\bgeri\b", re.I), ActionKind.MOVE, -1.0),
    (re.compile(r"\b(?:sol|sola)\b", re.I), ActionKind.TURN, 1.0),
    (re.compile(r"\b(?:sağ|sağa)\b", re.I), ActionKind.TURN, -1.0),
)


def parse_command(text: str) -> RobotAction | None:
    """Parse supported Turkish text; return None instead of guessing."""
    cleaned = _clean(text)
    if not cleaned:
        return None
    if STOP_RE.search(cleaned):
        return RobotAction(ActionKind.STOP)
    speech = SPEECH_RE.match(cleaned)
    if speech:
        return RobotAction(ActionKind.SPEAK, text=speech.group(1).strip())
    matches = _movement_matches(cleaned)
    if len(matches) != 1:
        return None
    kind, direction = matches[0]
    default = _default_value(kind)
    return RobotAction(kind, value=direction * _number(cleaned, default))


def _clean(text: str) -> str:
    stripped = ACTIVATION_RE.sub("", text.strip())
    return stripped.strip(" \t\n.,!?;:")


def _movement_matches(text: str) -> list[tuple[ActionKind, float]]:
    return [
        (kind, direction)
        for pattern, kind, direction in MOVEMENT_PATTERNS
        if pattern.search(text)
    ]


def _default_value(kind: ActionKind) -> float:
    if kind is ActionKind.MOVE:
        return DEFAULT_DISTANCE_MM
    return DEFAULT_TURN_DEGREES


def _number(text: str, default: float) -> float:
    match = NUMBER_RE.search(text)
    if match is None:
        return default
    return float(match.group(1).replace(",", "."))
