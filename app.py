"""Run the local browser interface."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

from src.model import create_population, summarize_population, validate_scenario


ROOT = Path(__file__).resolve().parent


class AppHandler(BaseHTTPRequestHandler):
    def send_body(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data, status=200):
        self.send_body(json.dumps(data, allow_nan=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self.send_body((ROOT / "web/index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/scenario":
            scenario = json.loads((ROOT / "scenarios/example.json").read_text(encoding="utf-8"))
            self.send_json(validate_scenario(scenario))
        elif path == "/favicon.ico":
            self.send_body(b"", "image/x-icon", 204)
        else:
            self.send_json({"error": "Page not found."}, 404)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/population":
            self.send_json({"error": "Page not found."}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("Send a settings file smaller than 64 KB.")
            scenario = validate_scenario(json.loads(self.rfile.read(length)))
            people = create_population(scenario)
            self.send_json({"scenario": scenario, **summarize_population(people, scenario)})
        except ValueError as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), AppHandler) as server:
            print(f"Open http://127.0.0.1:{args.port}", flush=True)
            print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
    except OSError as error:
        parser.error(f"Could not start the app: {error}. Try --port 8001.")


if __name__ == "__main__":
    main()
