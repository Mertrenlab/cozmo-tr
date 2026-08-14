"""Run the protected Cozmo dashboard on a loopback HTTP server.

Responsible for: sockets, request translation, browser launch, and teardown.
Not responsible for: request routing, robot decisions, or remote hosting.
"""

import logging
import secrets
import webbrowser
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cozmo_tr.dashboard_api import DashboardApi, HttpResponse
from cozmo_tr.dashboard_service import DashboardService

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_REQUEST_BYTES = 16_384
logger = logging.getLogger(__name__)


class DashboardHandler(BaseHTTPRequestHandler):
    """Translate socket requests into the HTTP-neutral dashboard API."""

    api: DashboardApi

    def do_GET(self) -> None:  # noqa: N802
        """Serve one static, status, capability, or photo response."""
        self._write(self.api.handle_get(self.path))

    def do_POST(self) -> None:  # noqa: N802
        """Read one bounded JSON body and serve its protected response."""
        length = _content_length(dict(self.headers.items()))
        if length is None:
            self._write(_error(400, "Geçersiz içerik uzunluğu."))
            return
        if length > MAX_REQUEST_BYTES:
            self._write(_error(413, "İstek çok büyük."))
            return
        body = self.rfile.read(length)
        headers = dict(self.headers.items())
        self._write(self.api.handle_post(self.path, headers, body))

    def log_message(self, template: str, *args: object) -> None:
        """Route server access lines through project logging."""
        logger.info("dashboard_request", extra={"detail": template % args})

    def _write(self, response: HttpResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", _content_security_policy())
        self.end_headers()
        self.wfile.write(response.body)


def create_dashboard_server(
    api: DashboardApi, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT
) -> ThreadingHTTPServer:
    """Bind a dashboard handler to the loopback host and requested port."""

    class BoundHandler(DashboardHandler):
        pass

    BoundHandler.api = api
    server = ThreadingHTTPServer((host, port), BoundHandler)
    server.daemon_threads = True
    return server


def run_dashboard(port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    """Start one protected local dashboard until the process is interrupted."""
    token = secrets.token_urlsafe(32)
    api = DashboardApi(DashboardService(), token)
    server = create_dashboard_server(api, port=port)
    actual_port = server.server_address[1]
    url = f"http://{DEFAULT_HOST}:{actual_port}/"
    if open_browser:
        webbrowser.open(url)
    logger.info("dashboard_ready", extra={"url": url})
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        logger.info("dashboard_stopped")
    finally:
        server.server_close()
        api.close()


def _content_length(headers: Mapping[str, str]) -> int | None:
    raw = next(
        (value for key, value in headers.items() if key.casefold() == "content-length"),
        None,
    )
    try:
        return int(raw) if raw is not None else None
    except ValueError:
        return None


def _error(status: int, message: str) -> HttpResponse:
    body = f'{{"ok":false,"message":"{message}"}}'.encode()
    return HttpResponse(status, "application/json; charset=utf-8", body)


def _content_security_policy() -> str:
    return "default-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
