"""
Flujo OAuth2 interactivo de Raindrop.io.

Uso:
    python tools/raindrop_oauth.py

Requiere en .env:
    RAINDROP_CLIENT_ID
    RAINDROP_CLIENT_SECRET
    RAINDROP_REDIRECT_URI=http://localhost:8766/callback

Guarda tokens en artifacts/raindrop_state.json (gitignored).
"""

from __future__ import annotations

import os
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env
from tools.raindrop_tools import AUTH_URL, DEFAULT_REDIRECT, TOKEN_URL, save_initial_tokens

load_project_env(Path(__file__).resolve().parent.parent / ".env")


class CallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    error: str | None = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        CallbackHandler.code = (params.get("code") or [None])[0]
        CallbackHandler.error = (params.get("error") or [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if CallbackHandler.code:
            body = "<html><body><h2>Raindrop.io autorizado</h2><p>Ya puedes cerrar esta ventana.</p></body></html>"
        else:
            body = f"<html><body><h2>Error autorizando Raindrop.io</h2><p>{CallbackHandler.error}</p></body></html>"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        return


def _redirect_parts(uri: str) -> tuple[str, int]:
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise SystemExit("RAINDROP_REDIRECT_URI debe ser local, ej. http://localhost:8766/callback")
    return parsed.hostname, parsed.port or 80


def main() -> int:
    client_id = os.getenv("RAINDROP_CLIENT_ID", "").strip()
    client_secret = os.getenv("RAINDROP_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("RAINDROP_REDIRECT_URI", DEFAULT_REDIRECT).strip()

    if not client_id or not client_secret:
        print("Faltan RAINDROP_CLIENT_ID / RAINDROP_CLIENT_SECRET en .env")
        return 2

    host, port = _redirect_parts(redirect_uri)
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    print("Abriendo navegador para autorizar Coworkia en Raindrop.io...")
    print(f"Redirect URI: {redirect_uri}")
    server = HTTPServer((host, port), CallbackHandler)
    webbrowser.open(auth_url)

    server.timeout = 180
    while CallbackHandler.code is None and CallbackHandler.error is None:
        server.handle_request()

    if CallbackHandler.error:
        print(f"Autorizacion cancelada o fallida: {CallbackHandler.error}")
        return 1
    if not CallbackHandler.code:
        print("No se recibio code OAuth.")
        return 1

    resp = requests.post(
        TOKEN_URL,
        json={
            "grant_type": "authorization_code",
            "code": CallbackHandler.code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    save_initial_tokens(
        payload["access_token"],
        payload.get("refresh_token", ""),
        int(payload.get("expires_in", 1209600)),
    )
    print("Tokens guardados en artifacts/raindrop_state.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
