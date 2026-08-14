"""Command-line tests for dry-run and diagnostics."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from cozmo_tr.cli import main
from cozmo_tr.stt import SttUnavailable


class CliTests(unittest.TestCase):
    """Exercise user-visible commands without a robot."""

    def test_parse_prints_safe_json(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["parse", "ileri 999"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["kind"], "move")
        self.assertEqual(payload["value"], 150.0)

    def test_parse_unknown_returns_usage_error(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["parse", "bilmiyorum"])
        self.assertEqual(code, 2)
        self.assertIn("Anlayamadım", output.getvalue())

    def test_doctor_accepts_complete_fake_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "final.mdl").touch()
            output = StringIO()
            with redirect_stdout(output):
                code = main(["doctor", "--model", str(model)])
        self.assertEqual(code, 0)
        self.assertIn("[OK] Türkçe Vosk modeli", output.getvalue())

    def test_say_creates_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "voice.wav"
            output = StringIO()
            with redirect_stdout(output):
                code = main(["say", "Merhaba", "--output", str(output_path)])
            self.assertTrue(output_path.is_file())
        self.assertEqual(code, 0)
        self.assertIn("22050 Hz", output.getvalue())

    def test_run_once_uses_dry_run_robot(self) -> None:
        transcriber = Mock()
        transcriber.transcribe_once.return_value = "ileri 999"
        output = StringIO()
        with (
            patch("cozmo_tr.cli.VoskTranscriber", return_value=transcriber),
            redirect_stdout(output),
        ):
            code = main(["run", "--once"])
        self.assertEqual(code, 0)
        self.assertIn('"value": 150.0', output.getvalue())

    def test_run_loop_can_exit_without_recording(self) -> None:
        transcriber = Mock()
        with (
            patch("cozmo_tr.cli.VoskTranscriber", return_value=transcriber),
            patch("builtins.input", return_value="q"),
        ):
            code = main(["run"])
        self.assertEqual(code, 0)
        transcriber.transcribe_once.assert_not_called()

    def test_voice_error_is_actionable(self) -> None:
        output = StringIO()
        error = SttUnavailable("mikrofon yok")
        with (
            patch("cozmo_tr.cli.VoskTranscriber", side_effect=error),
            redirect_stdout(output),
        ):
            code = main(["run", "--once"])
        self.assertEqual(code, 1)
        self.assertIn("mikrofon yok", output.getvalue())

    def test_commands_lists_ball_and_direct_controls(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["commands"])
        self.assertEqual(code, 0)
        self.assertIn("topla oyna", output.getvalue())
        self.assertIn("başını kaldır", output.getvalue())

    def test_capabilities_exposes_honest_states_as_json(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main(["capabilities", "--json"])
        payload = json.loads(output.getvalue())
        ball = next(item for item in payload if item["id"] == "ball_play")
        self.assertEqual(code, 0)
        self.assertEqual(ball["state"], "hardware_pending")

    def test_execute_runs_one_typed_command_and_always_closes_robot(self) -> None:
        robot = Mock()
        output = StringIO()
        with (
            patch("cozmo_tr.cli.PyCozmoRobot", return_value=robot),
            redirect_stdout(output),
        ):
            code = main(["execute", "başını kaldır"])
        self.assertEqual(code, 0)
        robot.connect.assert_called_once_with()
        robot.execute.assert_called_once()
        robot.close.assert_called_once_with()
        self.assertIn("güvenle uygulandı", output.getvalue())

    def test_execute_rejects_unknown_text_without_robot_action(self) -> None:
        robot = Mock()
        with (
            patch("cozmo_tr.cli.PyCozmoRobot", return_value=robot),
            redirect_stdout(StringIO()),
        ):
            code = main(["execute", "ışınlan"])
        self.assertEqual(code, 2)
        robot.execute.assert_not_called()
        robot.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
