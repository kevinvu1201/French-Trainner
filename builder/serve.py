"""Local static server for dist/ (or dist-enc/)."""

from __future__ import annotations

import functools
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class _Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive: no new connection (and handshake) per file
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
        ".json": "application/json", ".webmanifest": "application/manifest+json",
        ".enc": "application/octet-stream", ".woff2": "font/woff2", ".png": "image/png",
    }

    def end_headers(self) -> None:
        # Development server: always revalidate; the service worker does the offline caching.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:  # quieter console
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)


def lan_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return None


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        # Browsers drop idle keep-alive connections; that isn't worth a traceback.
        if not isinstance(sys.exc_info()[1], (ConnectionResetError, ConnectionAbortedError, BrokenPipeError)):
            super().handle_error(request, client_address)


def make_server(root: Path, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    handler = functools.partial(_Handler, directory=str(root))
    return _Server((host, port), handler)


def serve(root: Path, host: str = "127.0.0.1", port: int = 8000) -> None:
    server = make_server(root, host, port)
    print(f"Serving {root} at http://localhost:{server.server_address[1]}/")
    if host in ("0.0.0.0", ""):
        ip = lan_ip()
        if ip:
            print(f"  on your network: http://{ip}:{server.server_address[1]}/  "
                  "(offline install needs HTTPS or localhost; use the deployed URL on your phone)")
    print("  Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
