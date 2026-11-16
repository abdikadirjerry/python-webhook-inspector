from src.storage import load_events

def query_events(method_filter: str = "", search_term: str = "") -> list[dict]:
    events = load_events()
    results = []
    term = search_term.lower().strip()
    method = method_filter.upper().strip()

    for evt in events:
        if method and method != "ALL" and evt["method"] != method:
            continue
        if term:
            haystack = f"{evt['endpoint']} {evt['source_ip']} {str(evt['payload'])}".lower()
            if term not in haystack:
                continue
        results.append(evt)
    return results

def compute_traffic_stats(events: list[dict]) -> dict:
    total = len(events)
    post_count = sum(1 for e in events if e["method"] == "POST")
    unique_endpoints = len({e["endpoint"] for e in events})
    json_count = sum(1 for e in events if "application/json" in e.get("content_type", ""))

    return {
        "total_captured": total,
        "post_requests": post_count,
        "unique_routes": unique_endpoints,
        "json_payloads": json_count
    }