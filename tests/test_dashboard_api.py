"""Tests for the local dashboard HTTP application boundary."""

import json
import tempfile
import unittest
from pathlib import Path

from cozmo_tr.actions import RobotAction
from cozmo_tr.dashboard_api import TOKEN_HEADER, DashboardApi
from cozmo_tr.dashboard_service import DashboardService


class FakeRobot:
    """Collect dashboard robot lifecycle and actions."""

    def __init__(self) -> None:
        self.connected = False
        self.actions: list[RobotAction] = []

    def connect(self) -> None:
        self.connected = True

    def execute(self, action: RobotAction) -> None:
        self.actions.append(action)

    def close(self) -> None:
        self.connected = False


class FakeTranscriber:
    """Return a command without touching the Mac microphone."""

    def transcribe_once(self, _seconds: float) -> str:
        return "mutlu ol"


class DashboardApiTests(unittest.TestCase):
    """Expose JSON and assets while protecting every mutating request."""

    def setUp(self) -> None:
        self.robot = FakeRobot()
        service = DashboardService(
            robot_factory=lambda: self.robot,
            transcriber_factory=FakeTranscriber,
        )
        self.assets = {
            "index.html": b"<meta data-token='__COZMO_TOKEN__'>Cozmo Kontrol Merkezi",
            "app.js": b"window.CozmoTR = true",
            "styles.css": b":root { color: white; }",
        }
        self.temp = tempfile.TemporaryDirectory()
        self.api = DashboardApi(
            service,
            token="secret-token",
            asset_loader=lambda name: self.assets[name],
            capture_dir=Path(self.temp.name),
        )

    def tearDown(self) -> None:
        self.api.close()
        self.temp.cleanup()

    def post(self, path: str, payload: object, token: str = "secret-token") -> object:
        """Send one authorized JSON request and decode its response."""
        headers = {TOKEN_HEADER: token, "Content-Type": "application/json"}
        body = json.dumps(payload).encode()
        return self.api.handle_post(path, headers, body)

    def test_serves_tokenized_page_assets_status_and_capabilities(self) -> None:
        page = self.api.handle_get("/")
        script = self.api.handle_get("/assets/app.js")
        root_script = self.api.handle_get("/app.js")
        root_styles = self.api.handle_get("/styles.css")
        status = self.api.handle_get("/api/status")
        capabilities = self.api.handle_get("/api/capabilities")
        self.assertIn(b"secret-token", page.body)
        self.assertEqual(script.content_type, "text/javascript; charset=utf-8")
        self.assertEqual(root_script.body, script.body)
        self.assertEqual(root_styles.content_type, "text/css; charset=utf-8")
        self.assertFalse(json.loads(status.body)["connected"])
        self.assertTrue(json.loads(capabilities.body)["capabilities"])

    def test_rejects_missing_token_content_type_and_bad_json(self) -> None:
        denied = self.post("/api/connect", {}, token="wrong")
        wrong_type = self.api.handle_post(
            "/api/connect", {TOKEN_HEADER: "secret-token"}, b"{}"
        )
        bad_json = self.api.handle_post(
            "/api/connect",
            {TOKEN_HEADER: "secret-token", "Content-Type": "application/json"},
            b"{",
        )
        self.assertEqual(denied.status, 403)
        self.assertEqual(wrong_type.status, 415)
        self.assertEqual(bad_json.status, 400)

    def test_connect_execute_listen_and_disconnect(self) -> None:
        self.assertEqual(self.post("/api/connect", {}).status, 200)
        executed = self.post("/api/execute", {"text": "ileri 999"})
        listened = self.post("/api/listen", {"seconds": 4})
        self.assertEqual(json.loads(executed.body)["action"]["value"], 150.0)
        self.assertEqual(json.loads(listened.body)["transcript"], "mutlu ol")
        self.assertEqual(self.post("/api/disconnect", {}).status, 200)
        self.assertFalse(self.robot.connected)

    def test_unknown_command_and_unconnected_command_are_clear(self) -> None:
        unconnected = self.post("/api/execute", {"text": "dur"})
        self.post("/api/connect", {})
        unknown = self.post("/api/execute", {"text": "ışınlan"})
        self.assertEqual(unconnected.status, 409)
        self.assertEqual(unknown.status, 422)

    def test_latest_photo_requires_token_and_stays_inside_capture_dir(self) -> None:
        photo = Path(self.temp.name) / "cozmo-20260815-001.jpg"
        photo.write_bytes(b"jpeg")
        denied = self.api.handle_get("/api/photo/latest")
        ready = self.api.handle_get("/api/photo/latest?token=secret-token")
        self.assertEqual(denied.status, 403)
        self.assertEqual(ready.body, b"jpeg")
        self.assertEqual(ready.content_type, "image/jpeg")

    def test_unknown_route_returns_not_found(self) -> None:
        self.assertEqual(self.api.handle_get("/nope").status, 404)
        self.assertEqual(self.post("/api/nope", {}).status, 404)


if __name__ == "__main__":
    unittest.main()
