from .cli import build_parser, main
from .scrape import load_config, scrape, to_float

__version__ = "0.1.0"
__all__ = ["app", "build_parser", "load_config", "main", "scrape", "to_float", "__version__"]


def __getattr__(name: str):
    if name == "app":
        from .app import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
