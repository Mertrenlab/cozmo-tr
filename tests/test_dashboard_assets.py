"""Contract tests for the packaged local control panel assets."""

import unittest
from importlib.resources import files


class DashboardAssetTests(unittest.TestCase):
    """Keep the first viewport and controls product-specific and accessible."""

    def test_page_contains_connection_command_voice_and_photo_surfaces(self) -> None:
        page = files("cozmo_tr.web").joinpath("index.html").read_text()
        for expected in (
            "Cozmo Kontrol Merkezi",
            "__COZMO_TOKEN__",
            'id="connect-button"',
            'id="stop-button"',
            'id="command-form"',
            'id="listen-button"',
            'id="camera-preview"',
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)

    def test_script_uses_only_the_protected_local_api(self) -> None:
        script = files("cozmo_tr.web").joinpath("app.js").read_text()
        self.assertIn("X-Cozmo-Token", script)
        self.assertIn("/api/connect", script)
        self.assertIn("/api/status", script)
        self.assertIn("/api/execute", script)
        self.assertIn("/api/listen", script)
        self.assertNotIn("http://", script)
        self.assertNotIn("https://", script)


if __name__ == "__main__":
    unittest.main()
