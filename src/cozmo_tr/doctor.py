"""Inspect local prerequisites before switching to Cozmo's offline Wi-Fi.

Responsible for: actionable, side-effect-free environment diagnostics.
Not responsible for: installing packages, downloading models, or robot motion.
"""

import importlib.util
import shutil
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ToolProbe = Callable[[str], str | None]
ModuleProbe = Callable[[str], bool]


@dataclass(frozen=True, slots=True)
class Check:
    """Describe one prerequisite and how severe its absence is."""

    name: str
    ok: bool
    required: bool
    detail: str


def inspect_environment(
    model: Path,
    tool_probe: ToolProbe = shutil.which,
    module_probe: ModuleProbe | None = None,
    platform: str = sys.platform,
) -> tuple[Check, ...]:
    """Return deterministic checks without modifying the host."""
    has_module = module_probe or _has_module
    checks = [_model_check(model)]
    checks.extend(_tts_checks(tool_probe, platform))
    checks.extend(
        (
            _module_check("Vosk Python paketi", "vosk", True, has_module),
            _module_check("Mikrofon paketi", "sounddevice", True, has_module),
            _module_check("PyCozmo", "pycozmo", False, has_module),
        )
    )
    return tuple(checks)


def report_ok(checks: Sequence[Check]) -> bool:
    """Return True when every required prerequisite is available."""
    return all(check.ok or not check.required for check in checks)


def format_report(checks: Sequence[Check]) -> str:
    """Render checks as concise Turkish status lines."""
    return "\n".join(f"[{_label(check)}] {check.name}: {check.detail}" for check in checks)


def _model_check(model: Path) -> Check:
    ready = (model / "final.mdl").is_file() or (model / "am" / "final.mdl").is_file()
    detail = str(model) if ready else "Modeli Cozmo Wi-Fi'ye geçmeden önce indirin"
    return Check("Türkçe Vosk modeli", ready, True, detail)


def _tts_checks(tool_probe: ToolProbe, platform: str) -> list[Check]:
    if platform != "darwin":
        return [Check("macOS Türkçe TTS", False, True, "Bu MVP macOS gerektirir")]
    return [
        _tool_check("macOS say", "say", tool_probe),
        _tool_check("WAV dönüştürücü", "afconvert", tool_probe),
    ]


def _tool_check(name: str, executable: str, probe: ToolProbe) -> Check:
    path = probe(executable)
    return Check(name, path is not None, True, path or f"{executable} bulunamadı")


def _module_check(name: str, module: str, required: bool, probe: ModuleProbe) -> Check:
    available = probe(module)
    detail = "kurulu" if available else f"pip install ile {module} kurun"
    return Check(name, available, required, detail)


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _label(check: Check) -> str:
    if check.ok:
        return "OK"
    return "HATA" if check.required else "UYARI"
