import json
from playwright.sync_api import sync_playwright

with open("config.json", "r") as f:
    config = json.load(f)

def scrape() -> tuple[dict, int]:
    price_result = {}
    url = config.get("url").get("izko")
    labels = config.get("label")
    if not url: return {"error": "URL param is required"}, 400

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(f'#{labels.get("Cumhuriyet", "ataLabel")}', timeout=15000)

        for name, id_ in labels.items():
            element = page.query_selector(f"#{id_}")
            price_result[name] = to_float(element.inner_text().strip()) if element else None

    return {
        "url": url,
        "priceList": price_result
    }, 200

def to_float(value: str) -> float | str:
    try:
        return float(value.replace(".", "")
                     .replace(",", "."))
    except (ValueError, AttributeError):
        return value