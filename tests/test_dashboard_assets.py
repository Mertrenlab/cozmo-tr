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

    def test_page_supports_file_preview_and_a_dedicated_drive_mode(self) -> None:
        page = files("cozmo_tr.web").joinpath("index.html").read_text()
        for expected in (
            'href="styles.css"',
            'src="app.js"',
            'id="file-preview"',
            'id="drive-mode-button"',
            'id="drive-dialog"',
            'data-drive-key="ArrowUp"',
            'data-drive-key="Space"',
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)

    def test_script_maps_keyboard_drive_controls_to_safe_commands(self) -> None:
        script = files("cozmo_tr.web").joinpath("app.js").read_text()
        for expected in (
            "window.location.protocol === 'file:'",
            "ArrowUp: 'ileri 50'",
            "ArrowDown: 'geri 50'",
            "ArrowLeft: 'sola 45'",
            "ArrowRight: 'sağa 45'",
            "Space: 'dur'",
            "KeyW: 'ileri 50'",
            "openDriveMode",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, script)


if __name__ == "__main__":
    unittest.main()
