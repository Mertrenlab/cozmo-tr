"""Tests for actionable environment diagnostics."""

import tempfile
import unittest
from pathlib import Path

from cozmo_tr.doctor import format_report, inspect_environment, report_ok


class DoctorTests(unittest.TestCase):
    """Check required failures and optional robot readiness separately."""

    def test_reports_ready_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "final.mdl").touch()
            checks = inspect_environment(
                model,
                tool_probe=lambda _name: "/usr/bin/tool",
                module_probe=lambda _name: True,
                platform="darwin",
            )
        self.assertTrue(report_ok(checks))
        self.assertTrue(all(check.ok for check in checks))

    def test_missing_model_is_required_failure(self) -> None:
        checks = inspect_environment(
            Path("/missing/model"),
            tool_probe=lambda _name: "/usr/bin/tool",
            module_probe=lambda _name: True,
            platform="darwin",
        )
        self.assertFalse(report_ok(checks))
        report = format_report(checks)
        self.assertIn("[HATA] Türkçe Vosk modeli", report)
        self.assertIn("Cozmo Wi-Fi", report)

    def test_missing_pycozmo_is_warning_not_core_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "final.mdl").touch()
            checks = inspect_environment(
                model,
                tool_probe=lambda _name: "/usr/bin/tool",
                module_probe=lambda name: name != "pycozmo",
                platform="darwin",
            )
        self.assertTrue(report_ok(checks))
        self.assertIn("[UYARI] PyCozmo", format_report(checks))

    def test_non_macos_is_required_tts_failure(self) -> None:
        checks = inspect_environment(
            Path("/missing/model"),
            tool_probe=lambda _name: None,
            module_probe=lambda _name: True,
            platform="linux",
        )
        self.assertIn("macOS gerektirir", format_report(checks))
        self.assertFalse(report_ok(checks))


if __name__ == "__main__":
    unittest.main()
