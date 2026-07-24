from __future__ import annotations

import argparse
import http.server
import json
import urllib.parse
import webbrowser
from typing import Any

import requests

TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"
SCOPE = "user-read-recently-played"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

auth_code: str | None = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):  # noqa: N801
    def do_GET(self) -> None:  # noqa: N802
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        if "code" in params:
            auth_code = params["code"][0]
            body = "<html><body><h1>Auth successful!</h1><p>Close this tab.</p></body></html>"
            self.wfile.write(body.encode())
        else:
            body = f"<html><body><h1>Auth failed</h1><p>Params: {params}</p></body></html>"
            self.wfile.write(body.encode())

    def log_message(self, *args: Any, **kwargs: Any) -> None:
        pass


def exchange_code(client_id: str, client_secret: str, code: str) -> dict[str, Any]:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    return dict(resp.json())


def main() -> None:
    parser = argparse.ArgumentParser(description="Get a Spotify OAuth refresh token")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()

    authorize_url = (
        f"{AUTH_URL}?client_id={args.client_id}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )

    print("Opening browser for Spotify authorization...")
    print(f"If the browser doesn't open, visit:\n{authorize_url}\n")
    webbrowser.open(authorize_url)

    server = http.server.HTTPServer(("localhost", args.port), CallbackHandler)
    print(f"Listening on http://localhost:{args.port}/callback ...")
    while auth_code is None:
        server.handle_request()

    print("Authorization code received. Exchanging for tokens...")
    token_data = exchange_code(args.client_id, args.client_secret, auth_code)
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        print("Error: no refresh_token in response:")
        print(json.dumps(token_data, indent=2))
        return

    print("\n" + "=" * 60)
    print("REFRESH TOKEN (add to terraform.tfvars):")
    print(f'spotify_refresh_token = "{refresh_token}"')
    print("=" * 60)
    print("\nAlso set in your .env file:")
    print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")


if __name__ == "__main__":
    main()
