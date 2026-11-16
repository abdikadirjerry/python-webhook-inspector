# Python Webhook Inspector (`python-webhook-inspector`)

A zero-dependency Python web application and HTTP webhook capture engine that intercepts incoming webhook requests, parses headers and JSON payloads, and provides a real-time split-pane inspection dashboard.

## Features

- **Wildcard Webhook Ingestion:** Accepts `POST`, `PUT`, and `PATCH` requests on any `/webhook/<route>` path.
- **Split-Pane Inspection UI:** Inspect HTTP headers, source IPs, and formatted JSON payloads side-by-side.
- **Built-in Simulator & cURL Export:** Test payloads instantly or copy one-click `curl` replay commands.

## Quick Start

```bash
python3 run.py
```
