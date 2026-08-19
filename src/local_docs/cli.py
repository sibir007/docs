"""Command-line entry point for the local-docs package."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from local_docs.config import AppConfig
from local_docs.server import run_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve downloaded documentation locally")
    parser.add_argument("--host", default=None, help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--sites-dir", type=Path, default=None)
    parser.add_argument("--open-browser", dest="open_browser", action="store_true")
    parser.add_argument("--no-browser", dest="open_browser", action="store_false")
    parser.set_defaults(open_browser=None)
    parser.add_argument("--log-level", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = AppConfig.from_environment(
        bind_host=args.host,
        preferred_port=args.port,
        sites_dir=args.sites_dir,
        open_browser=args.open_browser,
        log_level=args.log_level,
    )
    logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO))
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Server stopped")
    except PermissionError as error:
        print(error, file=sys.stderr)
        return 1
    return 0
