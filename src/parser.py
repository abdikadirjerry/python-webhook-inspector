import json
import uuid
from datetime import datetime

def build_event_record(method: str, endpoint: str, source_ip: str, headers: dict, raw_body: bytes) -> dict:
    decoded_body = raw_body.decode("utf-8", errors="replace").strip()
    content_type = headers.get("Content-Type", "text/plain")

    parsed_payload = decoded_body
    if "application/json" in content_type and decoded_body:
        try:
            parsed_payload = json.loads(decoded_body)
        except json.JSONDecodeError:
            parsed_payload = {"_raw_invalid_json": decoded_body}
    elif not decoded_body:
        parsed_payload = {"_note": "Empty request body"}

    return {
        "id": f"evt-{uuid.uuid4().hex[:6]}",
        "method": method,
        "endpoint": endpoint,
        "source_ip": source_ip,
        "content_type": content_type,
        "headers": dict(headers),
        "payload": parsed_payload,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }