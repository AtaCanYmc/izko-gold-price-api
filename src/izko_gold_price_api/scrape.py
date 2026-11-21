from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config(config_path: str | Path | None = None) -> dict:
    resolved = Path(config_path or os.environ.get("IZKO_CONFIG_PATH", DEFAULT_CONFIG_PATH))
    with open(resolved, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()


def scrape(url: str | None = None, timeout: int | None = None, cfg: dict | None = None) -> tuple[dict, int]:
    active_cfg = cfg or config
    price_result = {}
    target_url = url if url is not None else active_cfg["url"]["izko"]
    wait_timeout = timeout if timeout is not None else active_cfg["url"]["timeout"]
    labels = active_cfg["label"]
    if not target_url:
        return {"error": "URL param is required"}, 500

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(target_url)
        page.wait_for_selector(
            selector=f'#{labels.get("Cumhuriyet", "ataLabel")}',
            timeout=wait_timeout,
        )

        for name, id_ in labels.items():
            element = page.query_selector(f"#{id_}")
            price_result[name] = to_float(element.inner_text().strip()) if element else None

    return {
        "url": target_url,
        "priceList": price_result,
    }, 200


def to_float(value: str) -> float | str:
    try:
        return float(value.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return value
