"""Recognize direct cube and charger commands before generic robot lights."""

import re

from cozmo_tr.actions import ActionKind, RobotAction

COLORS = {
    "kırmızı": "red",
    "yeşil": "green",
    "mavi": "blue",
    "beyaz": "white",
}
CUBE_RE = re.compile(r"\bküp(?:ü|ün)?\b", re.I)
CHARGER_RE = re.compile(r"\bşarj(?: istasyonu| ışığı| ışığını)?\b", re.I)
COUNT_RE = re.compile(r"\b(?:kaç küp|küpleri bul)\b", re.I)
OFF_RE = re.compile(r"\b(?:kapat|söndür)\b", re.I)


def parse_accessory_command(text: str) -> RobotAction | None:
    """Return one named accessory action or None for unrelated text."""
    if COUNT_RE.search(text):
        return RobotAction(ActionKind.ACCESSORY, text="cube_count")
    target = _target(text)
    if target is None:
        return None
    color = _color(text)
    if color is None and OFF_RE.search(text):
        color = "off"
    if color is None:
        return None
    return RobotAction(ActionKind.ACCESSORY, text=f"{target}_{color}")


def _target(text: str) -> str | None:
    if CUBE_RE.search(text):
        return "cube"
    if CHARGER_RE.search(text):
        return "charger"
    return None


def _color(text: str) -> str | None:
    for Turkish, value in COLORS.items():
        if re.search(rf"\b{Turkish}\b", text, re.I):
            return value
    return None
