import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from src.storage import save_event, clear_all_events
from src.parser import build_event_record
from src.inspector import query_events, compute_traffic_stats
from src.simulator import trigger_simulated_webhook

class WebhookInspectorHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath: Path, content_type: str):
        if not filepath.exists():
            self.send_error(404, "File Not Found")
            return
        content = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _capture_incoming_webhook(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b""
        source_ip = self.client_address[0]

        event = build_event_record(
            method=self.command,
            endpoint=parsed.path,
            source_ip=source_ip,
            headers=self.headers,
            raw_body=raw_body
        )
        save_event(event)
        self._send_json({"received": True, "event_id": event["id"]}, 202)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(Path("templates/index.html"), "text/html; charset=utf-8")
        elif parsed.path == "/static/app.js":
            self._send_file(Path("templates/app.js"), "application/javascript; charset=utf-8")
        elif parsed.path == "/api/events":
            qs = parse_qs(parsed.query)
            method = qs.get("method", ["ALL"])[0]
            q = qs.get("q", [""])[0]
            events = query_events(method, q)
            stats = compute_traffic_stats(events)
            self._send_json({"events": events, "stats": stats})
        else:
            self.send_error(404, "Route Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/simulate":
            created = trigger_simulated_webhook()
            self._send_json(created, 201)
        elif parsed.path.startswith("/webhook/"):
            self._capture_incoming_webhook()
        else:
            self.send_error(404, "Route Not Found")

    def do_PUT(self):
        if urlparse(self.path).path.startswith("/webhook/"):
            self._capture_incoming_webhook()
        else:
            self.send_error(404, "Route Not Found")

    def do_PATCH(self):
        if urlparse(self.path).path.startswith("/webhook/"):
            self._capture_incoming_webhook()
        else:
            self.send_error(404, "Route Not Found")

    def do_DELETE(self):
        if urlparse(self.path).path == "/api/events":
            clear_all_events()
            self._send_json({"cleared": True})
        else:
            self.send_error(404, "Route Not Found")

def run(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), WebhookInspectorHandler)
    print(f"[*] HookLens Webhook Inspector listening at http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run()