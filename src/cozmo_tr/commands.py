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

FIXED_PATTERNS: tuple[tuple[re.Pattern[str], RobotAction], ...] = (
    (
        re.compile(r"\b(?:kafa|ön) ışığını aç\b", re.I),
        RobotAction(ActionKind.HEADLIGHT, 1.0),
    ),
    (
        re.compile(r"\b(?:kafa|ön) ışığını kapat\b", re.I),
        RobotAction(ActionKind.HEADLIGHT, 0.0),
    ),
    (
        re.compile(r"\bbaşını (?:kaldır|yukarı)\b", re.I),
        RobotAction(ActionKind.HEAD, 35.0),
    ),
    (
        re.compile(r"\bbaşını (?:indir|aşağı)\b", re.I),
        RobotAction(ActionKind.HEAD, -20.0),
    ),
    (re.compile(r"\bbaşını ortala\b", re.I), RobotAction(ActionKind.HEAD, 10.0)),
    (
        re.compile(r"\bkolunu (?:kaldır|yukarı)\b", re.I),
        RobotAction(ActionKind.LIFT, 92.0),
    ),
    (
        re.compile(r"\bkolunu (?:indir|aşağı)\b", re.I),
        RobotAction(ActionKind.LIFT, 32.0),
    ),
    (re.compile(r"\bkolunu ortala\b", re.I), RobotAction(ActionKind.LIFT, 62.0)),
    (
        re.compile(r"\bışık(?:ları|larını) kapat\b", re.I),
        RobotAction(ActionKind.LIGHTS, text="off"),
    ),
    (
        re.compile(r"\bışık(?:ları|larını).*kırmızı\b", re.I),
        RobotAction(ActionKind.LIGHTS, text="red"),
    ),
    (
        re.compile(r"\bışık(?:ları|larını).*yeşil\b", re.I),
        RobotAction(ActionKind.LIGHTS, text="green"),
    ),
    (
        re.compile(r"\bışık(?:ları|larını).*mavi\b", re.I),
        RobotAction(ActionKind.LIGHTS, text="blue"),
    ),
    (
        re.compile(r"\bışık(?:ları|larını).*beyaz\b", re.I),
        RobotAction(ActionKind.LIGHTS, text="white"),
    ),
    (re.compile(r"\bmutlu ol\b", re.I), RobotAction(ActionKind.FACE, text="happy")),
    (re.compile(r"\büzgün ol\b", re.I), RobotAction(ActionKind.FACE, text="sad")),
    (re.compile(r"\bşaşır\b", re.I), RobotAction(ActionKind.FACE, text="surprised")),
    (re.compile(r"\bkızgın ol\b", re.I), RobotAction(ActionKind.FACE, text="angry")),
    (re.compile(r"\bnormal bak\b", re.I), RobotAction(ActionKind.FACE, text="neutral")),
    (
        re.compile(r"\bfotoğraf çek\b", re.I),
        RobotAction(ActionKind.CAMERA, text="capture"),
    ),
    (
        re.compile(r"\b(?:pil|batarya).*(?:durum|ne kadar|kaç)\b", re.I),
        RobotAction(ActionKind.STATUS, text="battery"),
    ),
    (
        re.compile(r"\bsesini (?:kapat|sustur)\b", re.I),
        RobotAction(ActionKind.VOLUME, 0.0),
    ),
    (
        re.compile(r"\bsesini (?:kıs|azalt)\b", re.I),
        RobotAction(ActionKind.VOLUME, 35.0),
    ),
    (
        re.compile(r"\bsesini (?:aç|yükselt)\b", re.I),
        RobotAction(ActionKind.VOLUME, 100.0),
    ),
    (re.compile(r"\bdans et\b", re.I), RobotAction(ActionKind.ROUTINE, text="dance")),
    (
        re.compile(r"\b(?:selam ver|merhaba|selam)\b", re.I),
        RobotAction(ActionKind.ROUTINE, text="greet"),
    ),
    (
        re.compile(r"\bkafanı salla\b", re.I),
        RobotAction(ActionKind.ROUTINE, text="nod"),
    ),
    (
        re.compile(r"\b(?:görüşürüz|hoşça kal|bay bay)\b", re.I),
        RobotAction(ActionKind.ROUTINE, text="goodbye"),
    ),
    (re.compile(r"\btopu bul\b", re.I), RobotAction(ActionKind.BALL, text="find")),
    (re.compile(r"\btopla oyna\b", re.I), RobotAction(ActionKind.BALL, text="play")),
    (
        re.compile(r"\b(?:nasılsın|iyi misin)\b", re.I),
        RobotAction(ActionKind.SPEAK, text="İyiyim, teşekkür ederim."),
    ),
    (
        re.compile(r"\b(?:adın ne|ismin ne|kimsin)\b", re.I),
        RobotAction(ActionKind.SPEAK, text="Ben Cozmo."),
    ),
    (
        re.compile(r"\b(?:şaka|espri|güldür)\b", re.I),
        RobotAction(
            ActionKind.SPEAK, text="Robotlar neden yorulmaz? Çünkü şarj olurlar!"
        ),
    ),
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
    fixed = _fixed_action(cleaned)
    if fixed is not None:
        return fixed
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


def _fixed_action(text: str) -> RobotAction | None:
    for pattern, action in FIXED_PATTERNS:
        if pattern.search(text):
            return action
    return None


def _default_value(kind: ActionKind) -> float:
    if kind is ActionKind.MOVE:
        return DEFAULT_DISTANCE_MM
    return DEFAULT_TURN_DEGREES


def _number(text: str, default: float) -> float:
    match = NUMBER_RE.search(text)
    if match is None:
        return default
    return float(match.group(1).replace(",", "."))
