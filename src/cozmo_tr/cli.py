"""Expose diagnostics, dry-run parsing, TTS, and push-to-talk commands.

Responsible for: CLI validation and Turkish user messages.
Not responsible for: domain safety decisions or hardware implementation.
"""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, cast

from cozmo_tr.actions import RobotAction, SafetyPolicy, UnsafeAction
from cozmo_tr.capabilities import capability_payloads, command_lines
from cozmo_tr.commands import parse_command
from cozmo_tr.dashboard_http import run_dashboard
from cozmo_tr.doctor import format_report, inspect_environment, report_ok
from cozmo_tr.orchestrator import TurnService
from cozmo_tr.robot import PyCozmoRobot, RobotUnavailable
from cozmo_tr.stt import SttUnavailable, VoskTranscriber
from cozmo_tr.tts import MacSayTts, TtsUnavailable

DEFAULT_MODEL = Path("models/vosk-model-small-tr-0.3")
DEFAULT_WAV = Path("cozmo-tr.wav")


class _ManagedRobot(Protocol):
    def connect(self) -> None: ...
    def execute(self, action: RobotAction) -> None: ...
    def close(self) -> None: ...


class DryRunRobot:
    """Print bounded actions without touching hardware."""

    def connect(self) -> None:
        """Satisfy the managed port without external state."""

    def execute(self, action: RobotAction) -> None:
        """Print one safe action as JSON."""
        print(json.dumps(_action_payload(action), ensure_ascii=False))

    def close(self) -> None:
        """Satisfy the managed port without external state."""


def build_parser() -> argparse.ArgumentParser:
    """Create the complete CLI grammar."""
    parser = argparse.ArgumentParser(prog="cozmo-tr")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Kurulum önkoşullarını kontrol et")
    doctor.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parse = commands.add_parser("parse", help="Türkçe komutu güvenli dry-run yap")
    parse.add_argument("text")
    say = commands.add_parser("say", help="Türkçe Cozmo WAV dosyası üret")
    say.add_argument("text")
    say.add_argument("--output", type=Path, default=DEFAULT_WAV)
    execute = commands.add_parser(
        "execute", help="Yazılı bir Türkçe komutu gerçek Cozmo'da çalıştır"
    )
    execute.add_argument("text")
    run = commands.add_parser("run", help="Mikrofondan bir veya çok komut dinle")
    run.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    run.add_argument("--seconds", type=float, default=4.0)
    run.add_argument("--robot", action="store_true")
    run.add_argument("--once", action="store_true")
    commands.add_parser("commands", help="Desteklenen Türkçe komutları listele")
    capabilities = commands.add_parser(
        "capabilities", help="Yeteneklerin doğrulama durumunu göster"
    )
    capabilities.add_argument("--json", action="store_true")
    dashboard = commands.add_parser("dashboard", help="Yerel kontrol panelini aç")
    dashboard.add_argument("--port", type=int, default=8765)
    dashboard.add_argument("--no-browser", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one CLI command and return a process exit code."""
    args = build_parser().parse_args(argv)
    command = cast(str, args.command)
    try:
        if command == "doctor":
            return _doctor(cast(Path, args.model))
        if command == "parse":
            return _parse(cast(str, args.text))
        if command == "say":
            return _say(cast(str, args.text), cast(Path, args.output))
        if command == "execute":
            return _execute(cast(str, args.text))
        if command == "commands":
            return _commands()
        if command == "capabilities":
            return _capabilities(cast(bool, args.json))
        return _runtime(command, args)
    except (RobotUnavailable, SttUnavailable, TtsUnavailable) as error:
        print(f"Hata: {error}")
        return 1


def _doctor(model: Path) -> int:
    checks = inspect_environment(model)
    print(format_report(checks))
    return 0 if report_ok(checks) else 1


def _parse(text: str) -> int:
    action = parse_command(text)
    if action is None:
        print("Anlayamadım. Örnek: ileri 50, geri 50, sola 30, sağa 30 veya dur.")
        return 2
    try:
        safe = SafetyPolicy().enforce(action)
    except UnsafeAction as error:
        print(f"Komut güvenli değil: {error}")
        return 2
    print(json.dumps(_action_payload(safe), ensure_ascii=False))
    return 0


def _say(text: str, output: Path) -> int:
    spec = MacSayTts().synthesize(text, output)
    print(f"Hazır: {output} ({spec.sample_rate} Hz, mono, 16-bit)")
    return 0


def _execute(text: str) -> int:
    robot = PyCozmoRobot()
    robot.connect()
    try:
        result = TurnService(robot).handle(text)
        print(result.message)
        return 0 if result.accepted else 2
    finally:
        robot.close()


def _commands() -> int:
    print("\n".join(command_lines()))
    return 0


def _capabilities(as_json: bool) -> int:
    if as_json:
        print(json.dumps(capability_payloads(), ensure_ascii=False))
    else:
        print("\n".join(command_lines()))
    return 0


def _runtime(command: str, args: argparse.Namespace) -> int:
    if command == "dashboard":
        run_dashboard(
            port=cast(int, args.port), open_browser=not cast(bool, args.no_browser)
        )
        return 0
    return _run(args)


def _run(args: argparse.Namespace) -> int:
    robot = _make_robot(cast(bool, args.robot))
    transcriber = VoskTranscriber(cast(Path, args.model))
    seconds = cast(float, args.seconds)
    robot.connect()
    try:
        if cast(bool, args.once):
            return _listen_once(transcriber, TurnService(robot), seconds)
        return _listen_loop(transcriber, TurnService(robot), seconds)
    finally:
        robot.close()


def _make_robot(enabled: bool) -> _ManagedRobot:
    return PyCozmoRobot() if enabled else DryRunRobot()


def _listen_once(
    transcriber: VoskTranscriber, service: TurnService, seconds: float
) -> int:
    print(f"Dinliyorum ({seconds:g} saniye)...")
    text = transcriber.transcribe_once(seconds)
    print(f"Duydum: {text or '(sessizlik)'}")
    result = service.handle(text)
    print(result.message)
    return 0 if result.accepted else 2


def _listen_loop(
    transcriber: VoskTranscriber, service: TurnService, seconds: float
) -> int:
    while input("Dinlemek için Enter, çıkmak için q: ").strip().casefold() != "q":
        _listen_once(transcriber, service, seconds)
    return 0


def _action_payload(action: RobotAction) -> dict[str, str | float | None]:
    return {"kind": action.kind.value, "value": action.value, "text": action.text}
