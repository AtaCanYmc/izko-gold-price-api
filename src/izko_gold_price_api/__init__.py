from .cli import build_parser, main
from .mcp import handle_mcp_request, run_mcp_server
from .scrape import load_config, scrape, to_float

try:
    from .app import app
except ModuleNotFoundError:
    app = None  # type: ignore[assignment]

__version__ = "0.1.0"
__all__ = [
    "app",
    "build_parser",
    "handle_mcp_request",
    "load_config",
    "main",
    "run_mcp_server",
    "scrape",
    "to_float",
    "__version__",
]
