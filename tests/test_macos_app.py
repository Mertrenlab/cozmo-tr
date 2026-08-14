"""Contract tests for the double-clickable macOS dashboard launcher."""

import os
import plistlib
import unittest
from pathlib import Path

APP_ROOT = Path("Cozmo TR.app")
LAUNCHER = APP_ROOT / "Contents" / "MacOS" / "CozmoTRLauncher"
PLIST = APP_ROOT / "Contents" / "Info.plist"


class MacAppTests(unittest.TestCase):
    """Keep the Finder launcher portable and actionable."""

    def test_bundle_metadata_points_to_executable_launcher(self) -> None:
        metadata = plistlib.loads(PLIST.read_bytes())
        self.assertEqual(metadata["CFBundleName"], "Cozmo TR")
        self.assertEqual(metadata["CFBundleExecutable"], "CozmoTRLauncher")
        self.assertTrue(os.access(LAUNCHER, os.X_OK))

    def test_launcher_uses_relative_project_path_and_local_dashboard(self) -> None:
        script = LAUNCHER.read_text()
        self.assertIn(".venv/bin/cozmo-tr", script)
        self.assertIn("dashboard", script)
        self.assertIn("127.0.0.1:8765", script)
        self.assertNotIn("/Users/", script)
        self.assertIn("Kurulum eksik", script)


if __name__ == "__main__":
    unittest.main()
