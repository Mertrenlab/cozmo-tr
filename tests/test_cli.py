"""Command-line tests for dry-run and diagnostics."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from cozmo_tr.cli import main


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


if __name__ == "__main__":
    unittest.main()
