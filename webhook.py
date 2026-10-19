#!/usr/bin/env python3
"""Webhook reference implementation for the WhatsApp Cloud API."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


def verify_challenge(params: dict, expected_token: str):
    """Return the challenge when the verification request is valid, else None."""
    if params.get("hub.mode") != "subscribe":
        return None
    if params.get("hub.verify_token") != expected_token:
        return None
    return params.get("hub.challenge")


def verify_signature(raw_body: bytes, header: str | None, app_secret: str) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    provided = header.split("=", 1)[1]
    expected = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided, expected)


def parse_messages(payload: dict):
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                messages.append({
                    "id": message.get("id"),
                    "from": message.get("from"),
                    "type": message.get("type"),
                    "text": (message.get("text") or {}).get("body", ""),
                    "timestamp": message.get("timestamp"),
                })
    return messages


class Handler(BaseHTTPRequestHandler):
    verify_token = ""
    app_secret = ""

    def _text(self, status: int, body: str):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        from urllib.parse import parse_qs, urlparse
        params = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        challenge = verify_challenge(params, self.verify_token)
        if challenge is None:
            self._text(403, "forbidden")
        else:
            self._text(200, challenge)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        if not verify_signature(raw, self.headers.get("X-Hub-Signature-256"),
                                self.app_secret):
            self._text(401, "invalid signature")
            return
        payload = json.loads(raw or b"{}")
        for message in parse_messages(payload):
            print(f"message from {message['from']}: {message['text']}", flush=True)
        self._text(200, "ok")

    def log_message(self, *args):
        pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="WhatsApp webhook study server")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)

    if args.command == "serve":
        Handler.verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
        Handler.app_secret = os.environ.get("WHATSAPP_APP_SECRET", "")
        if not Handler.verify_token or not Handler.app_secret:
            print("set WHATSAPP_VERIFY_TOKEN and WHATSAPP_APP_SECRET", file=sys.stderr)
            return 2
        server = HTTPServer(("127.0.0.1", args.port), Handler)
        print(f"listening on http://127.0.0.1:{args.port}/webhook")
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
