from __future__ import annotations

import atexit
import copy
import json
import os
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
MAX_TIMEOUT_MS = 60000
MIN_TIMEOUT_MS = 100

# ponytail: thread-local persistent Playwright context + in-memory dict TTL cache;
# upgrade to Redis + browser pool if multi-worker process fleet needs shared cache.
_browser_local = threading.local()
_cache_lock = threading.Lock()
_response_cache: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}


def _parse_bool_env(val: str) -> bool:
    return val.strip().lower() in {"1", "true", "yes", "on"}


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    resolved = Path(config_path or os.environ.get("IZKO_CONFIG_PATH", DEFAULT_CONFIG_PATH))
    with open(resolved, "r", encoding="utf-8") as f:
        cfg: dict[str, Any] = json.load(f)

    cfg.setdefault("url", {})
    cfg.setdefault("api", {})
    cfg["url"].setdefault("cache_ttl", 30)

    if "IZKO_HOST" in os.environ and os.environ["IZKO_HOST"].strip():
        cfg["api"]["host"] = os.environ["IZKO_HOST"].strip()
    if "IZKO_PORT" in os.environ and os.environ["IZKO_PORT"].strip():
        cfg["api"]["port"] = int(os.environ["IZKO_PORT"].strip())
    if "IZKO_DEBUG" in os.environ and os.environ["IZKO_DEBUG"].strip():
        cfg["api"]["debug"] = _parse_bool_env(os.environ["IZKO_DEBUG"])
    if "IZKO_TIMEOUT" in os.environ and os.environ["IZKO_TIMEOUT"].strip():
        cfg["url"]["timeout"] = int(os.environ["IZKO_TIMEOUT"].strip())
    if "IZKO_CACHE_TTL" in os.environ and os.environ["IZKO_CACHE_TTL"].strip():
        cfg["url"]["cache_ttl"] = int(os.environ["IZKO_CACHE_TTL"].strip())

    return cfg


config = load_config()


def is_safe_http_url(url: str) -> bool:
    if not isinstance(url, str) or not url.strip():
        return False
    parsed = urlsplit(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _get_persistent_context():
    ctx = getattr(_browser_local, "context", None)
    browser = getattr(_browser_local, "browser", None)
    if ctx is not None and browser is not None:
        is_connected = getattr(browser, "is_connected", lambda: True)
        if is_connected():
            return ctx
        close_browser()

    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    new_context_fn = getattr(browser, "new_context", None)
    ctx = new_context_fn() if callable(new_context_fn) else browser
    _browser_local.playwright = pw
    _browser_local.browser = browser
    _browser_local.context = ctx
    return ctx


def close_browser() -> None:
    for attr, method in (("context", "close"), ("browser", "close"), ("playwright", "stop")):
        obj = getattr(_browser_local, attr, None)
        setattr(_browser_local, attr, None)
        if obj is not None:
            try:
                getattr(obj, method)()
            except Exception:
                pass


atexit.register(close_browser)


def clear_cache() -> None:
    with _cache_lock:
        _response_cache.clear()


def _is_timeout_exception(exc: BaseException) -> bool:
    if isinstance(exc, TimeoutError):
        return True
    return any(cls.__name__ == "TimeoutError" for cls in type(exc).__mro__)


def scrape(
    url: str | None = None,
    timeout: int | None = None,
    cfg: dict[str, Any] | None = None,
    cache_ttl: int | None = None,
    use_cache: bool = True,
) -> tuple[dict[str, Any], int]:
    active_cfg = cfg if cfg is not None else load_config()
    price_result: dict[str, float | str | None] = {}
    target_url = url if url is not None else active_cfg["url"]["izko"]
    wait_timeout = timeout if timeout is not None else active_cfg["url"]["timeout"]
    ttl = cache_ttl if cache_ttl is not None else active_cfg["url"].get("cache_ttl", 30)
    labels: dict[str, str] = active_cfg["label"]

    if not target_url:
        return {"error": "URL param is required", "code": "MISSING_URL"}, 500
    if not is_safe_http_url(target_url):
        return {"error": "Only http and https URLs are permitted", "code": "INVALID_URL"}, 400
    if not isinstance(wait_timeout, int) or isinstance(wait_timeout, bool) or not (MIN_TIMEOUT_MS <= wait_timeout <= MAX_TIMEOUT_MS):
        return {
            "error": f"Timeout must be an integer between {MIN_TIMEOUT_MS} and {MAX_TIMEOUT_MS} ms",
            "code": "INVALID_TIMEOUT",
        }, 400
    if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl < 0:
        return {"error": "Cache TTL must be a non-negative integer", "code": "INVALID_CACHE_TTL"}, 400

    cache_key = (target_url, tuple(sorted(labels.items())))
    if use_cache and ttl > 0:
        now = time.monotonic()
        with _cache_lock:
            cached_entry = _response_cache.get(cache_key)
            if cached_entry is not None:
                expires_at, cached_payload = cached_entry
                if now < expires_at:
                    return copy.deepcopy(cached_payload), 200
                _response_cache.pop(cache_key, None)

    page = None
    try:
        context = _get_persistent_context()
        page = context.new_page()
        page.goto(target_url, timeout=wait_timeout)
        page.wait_for_selector(
            selector=f'#{labels.get("Cumhuriyet", "ataLabel")}',
            timeout=wait_timeout,
        )

        for name, id_ in labels.items():
            element = page.query_selector(f"#{id_}")
            price_result[name] = to_float(element.inner_text().strip()) if element else None
    except Exception as exc:
        if _is_timeout_exception(exc):
            return {
                "error": "Upstream selector or navigation timed out",
                "code": "UPSTREAM_TIMEOUT",
                "url": target_url,
            }, 504
        close_browser()
        return {
            "error": "Upstream navigation or network failure",
            "code": "UPSTREAM_BAD_GATEWAY",
            "url": target_url,
        }, 502
    finally:
        if page is not None:
            try:
                page.close()
            except Exception:
                pass

    payload: dict[str, Any] = {
        "url": target_url,
        "priceList": price_result,
    }

    if use_cache and ttl > 0:
        with _cache_lock:
            _response_cache[cache_key] = (time.monotonic() + ttl, copy.deepcopy(payload))

    return payload, 200


def to_float(value: str) -> float | str:
    try:
        return float(value.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return value
