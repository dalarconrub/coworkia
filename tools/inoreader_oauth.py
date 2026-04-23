"""
Flujo OAuth2 interactivo de Inoreader (una sola vez).

Uso:
    python tools/inoreader_oauth.py

Que hace:
  1. Lee INOREADER_APP_ID, INOREADER_APP_KEY (y opcional INOREADER_REDIRECT_URI) de .env.
  2. Levanta un servidor HTTP local en el puerto del redirect_uri.
  3. Abre el navegador en la pagina de autorizacion de Inoreader.
  4. Captura el ?code= que devuelve Inoreader, lo intercambia por tokens.
  5. Persiste access_token + refresh_token en artifacts/inoreader_state.json.
  6. A partir de aqui inoreader_tools.py refresca tokens automaticamente.

Pre-requisito: la app debe estar aprobada en https://www.inoreader.com/developers/.
"""

from __future__ import annotations

import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests

from tools.env_utils import load_project_env
from tools.inoreader_tools import (
    AUTH_URL,
    DEFAULT_REDIRECT,
    TOKEN_URL,
    save_initial_tokens,
    user_info,
)

load_project_env(Path(__file__).resolve().parent.parent / ".env")


_received: dict = {}


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (firma requerida por BaseHTTPRequestHandler)
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _received["code"] = params.get("code", [None])[0]
        _received["state"] = params.get("state", [None])[0]
        _received["error"] = params.get("error", [None])[0]
        body = (
            "<html><body><h2>Inoreader autorizado</h2>"
            "<p>Puedes cerrar esta pestana y volver a la terminal.</p>"
            "</body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # silencia logs por consola
        return


def _serve_until_callback(host: str, port: int, timeout: int = 300) -> None:
    server = HTTPServer((host, port), _CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.time() + timeout
    try:
        while time.time() < deadline and "code" not in _received and "error" not in _received:
            time.sleep(0.3)
    finally:
        server.shutdown()
        server.server_close()


def main() -> int:
    app_id = os.getenv("INOREADER_APP_ID")
    app_key = os.getenv("INOREADER_APP_KEY")
    redirect_uri = os.getenv("INOREADER_REDIRECT_URI", DEFAULT_REDIRECT)
    if not app_id or not app_key:
        print("Faltan INOREADER_APP_ID / INOREADER_APP_KEY en .env")
        return 2

    parsed = urllib.parse.urlparse(redirect_uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8080

    csrf = secrets.token_urlsafe(16)
    auth_params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read",
        "state": csrf,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

    print(f"Abriendo navegador para autorizar Coworkia en Inoreader...")
    print(f"Si no se abre, copia esta URL manualmente:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    _serve_until_callback(host, port)

    if _received.get("error"):
        print(f"Error de autorizacion: {_received['error']}")
        return 1
    if not _received.get("code"):
        print("Timeout esperando el callback de Inoreader.")
        return 1
    if _received.get("state") != csrf:
        print("State CSRF no coincide. Aborta por seguridad.")
        return 1

    print("Codigo recibido. Intercambiando por tokens...")
    resp = requests.post(
        TOKEN_URL,
        data={
            "code": _received["code"],
            "redirect_uri": redirect_uri,
            "client_id": app_id,
            "client_secret": app_key,
            "scope": "read",
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Error intercambiando code -> tokens: {resp.status_code} {resp.text[:300]}")
        return 1

    payload = resp.json()
    save_initial_tokens(
        access_token=payload["access_token"],
        refresh_token=payload["refresh_token"],
        expires_in=payload.get("expires_in", 3600),
    )
    print("Tokens guardados en artifacts/inoreader_state.json")

    try:
        info = user_info()
        who = info.get("userName") or info.get("userEmail") or info.get("userId")
        print(f"OK. Conectado como: {who}")
        print("Limites de cuota (Zone 1/2 = 100/dia cada uno por app externa, no varia con Pro).")
    except Exception as exc:
        print(f"Tokens guardados pero la llamada de prueba fallo: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
