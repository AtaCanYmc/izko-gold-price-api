import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    config_path = Path(os.environ.get("IZKO_CONFIG_PATH", DEFAULT_CONFIG_PATH))
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()


def scrape() -> tuple[dict, int]:
    price_result = {}
    url = config["url"]["izko"]
    labels = config["label"]
    if not url:
        return {"error": "URL param is required"}, 500

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(
            selector=f'#{labels.get("Cumhuriyet", "ataLabel")}',
            timeout=config["url"]["timeout"],
        )

        for name, id_ in labels.items():
            element = page.query_selector(f"#{id_}")
            price_result[name] = to_float(element.inner_text().strip()) if element else None

    return {
        "url": url,
        "priceList": price_result,
    }, 200


def to_float(value: str) -> float | str:
    try:
        return float(value.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return value
