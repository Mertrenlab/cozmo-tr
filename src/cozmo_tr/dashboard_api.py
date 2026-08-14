"""Serve dashboard assets and a token-protected local JSON API.

Responsible for: HTTP-neutral request routing, validation, and responses.
Not responsible for: sockets, browser launch, or robot implementation.
"""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from cozmo_tr.actions import RobotAction
from cozmo_tr.capabilities import capability_payloads
from cozmo_tr.dashboard_service import DashboardError, DashboardService
from cozmo_tr.errors import RobotUnavailable
from cozmo_tr.stt import SttUnavailable
from cozmo_tr.tts import TtsUnavailable

TOKEN_HEADER = "X-Cozmo-Token"
JSON_TYPE = "application/json; charset=utf-8"
ASSET_TYPES = {
    "app.js": "text/javascript; charset=utf-8",
    "styles.css": "text/css; charset=utf-8",
}
AssetLoader = Callable[[str], bytes]


@dataclass(frozen=True, slots=True)
class HttpResponse:
    """Represent a complete local HTTP response without a socket dependency."""

    status: int
    content_type: str
    body: bytes


class DashboardApi:
    """Route local dashboard requests around one protected robot service."""

    def __init__(
        self,
        service: DashboardService,
        token: str,
        asset_loader: AssetLoader | None = None,
        capture_dir: Path = Path("captures"),
    ) -> None:
        self._service = service
        self._token = token
        self._asset_loader = asset_loader or _load_asset
        self._capture_dir = capture_dir

    def handle_get(self, target: str) -> HttpResponse:
        """Serve one public static/status route or protected latest photo."""
        parsed = urlsplit(target)
        if parsed.path == "/":
            return self._page()
        if parsed.path == "/api/status":
            return _json(
                200, {"service": "cozmo-tr", "connected": self._service.connected}
            )
        if parsed.path == "/api/capabilities":
            return _json(200, {"capabilities": capability_payloads()})
        if parsed.path == "/api/photo/latest":
            return self._photo(parse_qs(parsed.query).get("token", [""])[0])
        return self._asset_or_missing(parsed.path)

    def handle_post(
        self, target: str, headers: Mapping[str, str], body: bytes
    ) -> HttpResponse:
        """Validate one mutating JSON request before dispatching it."""
        denied = self._validate_post(headers)
        if denied is not None:
            return denied
        payload = _decode_payload(body)
        if isinstance(payload, HttpResponse):
            return payload
        try:
            return self._dispatch_post(urlsplit(target).path, payload)
        except DashboardError as error:
            return _json(error.status, {"ok": False, "message": str(error)})
        except (RobotUnavailable, SttUnavailable, TtsUnavailable) as error:
            return _json(500, {"ok": False, "message": str(error)})

    def close(self) -> None:
        """Close any active robot connection during server teardown."""
        self._service.close()

    def _dispatch_post(self, path: str, payload: Mapping[str, object]) -> HttpResponse:
        routes: dict[str, Callable[[Mapping[str, object]], HttpResponse]] = {
            "/api/connect": self._connect,
            "/api/disconnect": self._disconnect,
            "/api/execute": self._execute,
            "/api/listen": self._listen,
        }
        handler = routes.get(path)
        if handler is None:
            return _json(404, {"ok": False, "message": "Sayfa bulunamadı."})
        return handler(payload)

    def _connect(self, _payload: Mapping[str, object]) -> HttpResponse:
        self._service.connect()
        return _json(200, {"ok": True, "connected": True})

    def _disconnect(self, _payload: Mapping[str, object]) -> HttpResponse:
        self._service.disconnect()
        return _json(200, {"ok": True, "connected": False})

    def _execute(self, payload: Mapping[str, object]) -> HttpResponse:
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            return _json(400, {"ok": False, "message": "Türkçe komut boş olamaz."})
        result = self._service.execute(text)
        status = 200 if result.accepted else 422
        return _json(status, _turn_payload(result.message, result.action))

    def _listen(self, payload: Mapping[str, object]) -> HttpResponse:
        seconds = payload.get("seconds", 4.0)
        if not isinstance(seconds, (int, float)) or not 0 < seconds <= 10:
            return _json(400, {"ok": False, "message": "Dinleme süresi geçersiz."})
        turn = self._service.listen(float(seconds))
        status = 200 if turn.result.accepted else 422
        response = _turn_payload(turn.result.message, turn.result.action)
        response["transcript"] = turn.transcript
        return _json(status, response)

    def _validate_post(self, headers: Mapping[str, str]) -> HttpResponse | None:
        if _header(headers, TOKEN_HEADER) != self._token:
            return _json(403, {"ok": False, "message": "Geçersiz panel oturumu."})
        content_type = _header(headers, "Content-Type").split(";", maxsplit=1)[0]
        if content_type != "application/json":
            return _json(415, {"ok": False, "message": "Yalnız JSON kabul edilir."})
        return None

    def _page(self) -> HttpResponse:
        body = self._asset_loader("index.html").replace(
            b"__COZMO_TOKEN__", self._token.encode()
        )
        return HttpResponse(200, "text/html; charset=utf-8", body)

    def _asset_or_missing(self, path: str) -> HttpResponse:
        name = path.removeprefix("/assets/")
        content_type = ASSET_TYPES.get(name)
        if content_type is None or path != f"/assets/{name}":
            return _json(404, {"ok": False, "message": "Sayfa bulunamadı."})
        return HttpResponse(200, content_type, self._asset_loader(name))

    def _photo(self, token: str) -> HttpResponse:
        if token != self._token:
            return _json(403, {"ok": False, "message": "Geçersiz panel oturumu."})
        photos = sorted(self._capture_dir.glob("cozmo-*.jpg"))
        if not photos:
            return _json(404, {"ok": False, "message": "Henüz fotoğraf yok."})
        return HttpResponse(200, "image/jpeg", photos[-1].read_bytes())


def _decode_payload(body: bytes) -> Mapping[str, object] | HttpResponse:
    try:
        payload: object = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _json(400, {"ok": False, "message": "Geçersiz JSON."})
    if not isinstance(payload, dict):
        return _json(400, {"ok": False, "message": "JSON nesnesi gerekli."})
    return payload


def _turn_payload(message: str, action: RobotAction | None) -> dict[str, object]:
    value = None
    if action is not None:
        value = {"kind": action.kind.value, "value": action.value, "text": action.text}
    return {"ok": action is not None, "message": message, "action": value}


def _header(headers: Mapping[str, str], name: str) -> str:
    wanted = name.casefold()
    return next(
        (value for key, value in headers.items() if key.casefold() == wanted), ""
    )


def _json(status: int, payload: Mapping[str, object]) -> HttpResponse:
    return HttpResponse(
        status, JSON_TYPE, json.dumps(payload, ensure_ascii=False).encode()
    )


def _load_asset(name: str) -> bytes:
    return files("cozmo_tr.web").joinpath(name).read_bytes()
