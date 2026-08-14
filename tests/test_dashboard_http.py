"""Integration tests for the loopback dashboard HTTP server."""

import json
import threading
import unittest
import urllib.error
import urllib.request

from cozmo_tr.dashboard_http import create_dashboard_server

from cozmo_tr.dashboard_api import TOKEN_HEADER, DashboardApi
from cozmo_tr.dashboard_service import DashboardService


class FakeRobot:
    """Provide a no-hardware lifecycle for HTTP integration."""

    def connect(self) -> None:
        return None

    def execute(self, _action: object) -> None:
        return None

    def close(self) -> None:
        return None


class DashboardHttpTests(unittest.TestCase):
    """Send real loopback requests through the request handler."""

    def setUp(self) -> None:
        service = DashboardService(robot_factory=FakeRobot)
        self.api = DashboardApi(
            service,
            token="http-secret",
            asset_loader=lambda _name: b"<html>__COZMO_TOKEN__</html>",
        )
        self.server = create_dashboard_server(self.api, port=0)
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.api.close()
        self.thread.join(timeout=1.0)

    def test_serves_status_from_loopback(self) -> None:
        with urllib.request.urlopen(f"{self.base_url}/api/status") as response:
            payload = json.loads(response.read())
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        self.assertEqual(payload["service"], "cozmo-tr")

    def test_post_requires_session_token(self) -> None:
        request = urllib.request.Request(
            f"{self.base_url}/api/connect",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 403)

    def test_authorized_post_reaches_dashboard_service(self) -> None:
        request = urllib.request.Request(
            f"{self.base_url}/api/connect",
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                TOKEN_HEADER: "http-secret",
            },
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read())
        self.assertTrue(payload["connected"])


if __name__ == "__main__":
    unittest.main()
