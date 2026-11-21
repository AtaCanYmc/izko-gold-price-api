from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from .scrape import MAX_TIMEOUT_MS, MIN_TIMEOUT_MS, load_config, scrape

__version__ = "0.2.0"
DEFAULT_PROTOCOL_VERSION = "2024-11-05"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_izko_prices",
        "description": (
            "Scrape live gold and currency prices from the Izmir Jewelers Chamber (izko.org.tr). "
            "Optionally filter by a single asset field such as GramAltin, Ceyrek, Cumhuriyet, Dolar, or Euro."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "field": {
                    "type": "string",
                    "description": (
                        "Optional single field name from priceList "
                        "(22Ayar, 18Ayar, 14Ayar, GramAltin, Cumhuriyet, Ceyrek, Yarim, Ziynet, PaketliHas, Dolar, Euro, Tarih)."
                    ),
                },
                "timeout": {
                    "type": "integer",
                    "minimum": MIN_TIMEOUT_MS,
                    "maximum": MAX_TIMEOUT_MS,
                    "description": "Optional DOM selector wait timeout in milliseconds (default: 10000).",
                },
                "use_cache": {
                    "type": "boolean",
                    "description": "Whether to use the in-memory TTL response cache (default: true).",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_izko_config",
        "description": "Return active IZKO scraper URL, DOM label mappings, and API configuration.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]

RESOURCES: list[dict[str, Any]] = [
    {
        "uri": "izko://config",
        "name": "IZKO Active Configuration",
        "description": "Active target URL, selector timeout, DOM label IDs, and API configuration.",
        "mimeType": "application/json",
    },
    {
        "uri": "izko://prices",
        "name": "IZKO Live Gold and Currency Prices",
        "description": "Live gold and currency price bundle scraped from izko.org.tr.",
        "mimeType": "application/json",
    },
]


def _jsonrpc_result(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _jsonrpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_mcp_request(request: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any] | None:
    active_cfg = cfg or load_config()
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params") or {}

    if "id" not in request:
        return None

    if method == "initialize":
        client_protocol = params.get("protocolVersion") or DEFAULT_PROTOCOL_VERSION
        return _jsonrpc_result(
            req_id,
            {
                "protocolVersion": client_protocol,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                },
                "serverInfo": {
                    "name": "izko-gold-price-api",
                    "version": __version__,
                },
            },
        )

    if method == "ping":
        return _jsonrpc_result(req_id, {})

    if method == "tools/list":
        return _jsonrpc_result(req_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}

        if tool_name == "get_izko_config":
            return _jsonrpc_result(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(active_cfg, indent=2, ensure_ascii=False),
                        }
                    ],
                    "isError": False,
                },
            )

        if tool_name == "get_izko_prices":
            try:
                use_cache = arguments.get("use_cache", True)
                payload, status = scrape(
                    timeout=arguments.get("timeout"),
                    cfg=active_cfg,
                    use_cache=bool(use_cache),
                )
            except Exception:
                return _jsonrpc_result(
                    req_id,
                    {
                        "content": [{"type": "text", "text": "Scrape failed"}],
                        "isError": True,
                    },
                )

            if status != 200:
                return _jsonrpc_result(
                    req_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                        "isError": True,
                    },
                )

            field = arguments.get("field")
            if field:
                price_list = payload.get("priceList", {})
                if field not in price_list:
                    available = ", ".join(price_list.keys())
                    return _jsonrpc_result(
                        req_id,
                        {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Unknown field '{field}'. Available fields: {available}",
                                }
                            ],
                            "isError": True,
                        },
                    )
                result_obj = {"field": field, "value": price_list[field], "url": payload.get("url")}
                return _jsonrpc_result(
                    req_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(result_obj, ensure_ascii=False)}],
                        "isError": False,
                    },
                )

            return _jsonrpc_result(
                req_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, indent=2, ensure_ascii=False),
                        }
                    ],
                    "isError": False,
                },
            )

        return _jsonrpc_error(req_id, -32602, f"Unknown tool: {tool_name}")

    if method == "resources/list":
        return _jsonrpc_result(req_id, {"resources": RESOURCES})

    if method == "resources/read":
        uri = params.get("uri")
        if uri == "izko://config":
            return _jsonrpc_result(
                req_id,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(active_cfg, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            )
        if uri == "izko://prices":
            payload, status = scrape(cfg=active_cfg)
            if status != 200:
                return _jsonrpc_error(req_id, -32603, payload.get("error", "Upstream scrape failed"))
            return _jsonrpc_result(
                req_id,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(payload, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            )
        return _jsonrpc_error(req_id, -32602, f"Unknown resource URI: {uri}")

    return _jsonrpc_error(req_id, -32601, f"Method not found: {method}")


def run_mcp_server(
    config_path: str | None = None,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
) -> int:
    cfg = load_config(config_path)
    for raw_line in stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            err = _jsonrpc_error(None, -32700, f"Parse error: {exc}")
            stdout.write(json.dumps(err, ensure_ascii=False) + "\n")
            stdout.flush()
            continue

        response = handle_mcp_request(request, cfg=cfg)
        if response is not None:
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


def main() -> int:
    return run_mcp_server()


if __name__ == "__main__":
    raise SystemExit(main())
