import random
from src.parser import build_event_record
from src.storage import save_event

SAMPLE_SCENARIOS = [
    (
        "POST",
        "/webhook/payment-settled",
        "198.51.100.24",
        {"Content-Type": "application/json", "X-Signature": "sha256=9f86d081884c7d659a2feaa0c55ad015"},
        b'{"event": "charge.succeeded", "amount": 12900, "currency": "EUR", "status": "verified"}'
    ),
    (
        "PUT",
        "/webhook/deployment-status",
        "203.0.113.88",
        {"Content-Type": "application/json", "X-Deploy-Agent": "ArgoCD/2.11"},
        b'{"cluster": "eu-west-1", "service": "auth-api", "revision": "v2.4.1", "health": "Healthy"}'
    ),
    (
        "POST",
        "/webhook/security-alert",
        "192.0.2.15",
        {"Content-Type": "application/json", "X-Alert-Severity": "HIGH"},
        b'{"rule": "BruteForceSSH", "blocked_ip": "45.33.32.156", "attempts": 42}'
    )
]

def trigger_simulated_webhook() -> dict:
    method, endpoint, ip, headers, raw_body = random.choice(SAMPLE_SCENARIOS)
    record = build_event_record(method, endpoint, ip, headers, raw_body)
    return save_event(record)