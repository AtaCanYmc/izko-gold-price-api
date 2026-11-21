from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .mcp import run_mcp_server
from .scrape import DEFAULT_CONFIG_PATH, load_config, scrape

__version__ = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="izko-gold-price-api",
        description="Izmir Jewelers Chamber (IZKO) gold and currency scraper SDK, CLI, Flask REST API, and MCP server.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help=f"Path to custom config.json file (default: {DEFAULT_CONFIG_PATH}).",
    )

    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the Flask REST API server (default action when no subcommand is given).",
    )
    serve_parser.add_argument("--host", default=None, help="Bind host address override.")
    serve_parser.add_argument("--port", type=int, default=None, help="Bind port override.")
    serve_parser.add_argument(
        "--debug",
        dest="debug",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable Flask debug mode.",
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Fetch live rates once via headless Chromium and print JSON or a single field.",
    )
    scrape_parser.add_argument(
        "-f",
        "--field",
        default=None,
        help="Print only a specific field from priceList (e.g. GramAltin, Ceyrek, Dolar).",
    )
    scrape_parser.add_argument("--url", default=None, help="Override target IZKO URL.")
    scrape_parser.add_argument("--timeout", type=int, default=None, help="Selector timeout in milliseconds.")
    scrape_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output with 2-space indent.")

    subparsers.add_parser(
        "config",
        help="Print active configuration JSON and exit.",
    )

    subparsers.add_parser(
        "mcp",
        help="Start the Model Context Protocol (MCP) JSON-RPC 2.0 server over stdio.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config(args.config)

    command = args.command or "serve"

    if command == "config":
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return 0

    if command == "mcp":
        return run_mcp_server(config_path=args.config)

    if command == "scrape":
        payload, status = scrape(url=args.url, timeout=args.timeout, cfg=cfg)
        if status != 200:
            print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
            return 1
        if args.field:
            price_list = payload.get("priceList", {})
            if args.field not in price_list:
                available = ", ".join(price_list.keys())
                print(f"Error: Unknown field '{args.field}'. Available: {available}", file=sys.stderr)
                return 1
            print(price_list[args.field])
            return 0
        indent = 2 if args.pretty else None
        print(json.dumps(payload, indent=indent, ensure_ascii=False))
        return 0

    from .app import app

    host = getattr(args, "host", None) or cfg["api"]["host"]
    port = getattr(args, "port", None) or cfg["api"]["port"]
    debug_arg = getattr(args, "debug", None)
    debug = cfg["api"]["debug"] if debug_arg is None else debug_arg

    app.run(debug=debug, host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
