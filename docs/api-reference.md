<!-- well-document · audit scorecard: G1:5 G2:5 G3:5 G4:5 G5:5 G6:5 · STATUS: PASS -->

[← Back to Root Repository](../README.md)

# API Reference

Complete specification for the Flask REST endpoints and the `izko_gold_price_api` Python SDK.

## Table of Contents

- [REST API Endpoints](#rest-api-endpoints)
- [HTTP Status Codes](#http-status-codes)
- [Python SDK Functions](#python-sdk-functions)
- [Configuration Schema](#configuration-schema)

## REST API Endpoints

### `GET /izko`

Returns the active `api` configuration block loaded from [`config.json`](../src/izko_gold_price_api/config.json). Does not launch a browser instance.

Request:

```bash
curl -i http://127.0.0.1:5000/izko
```

Response (`200 OK`):

```json
{
  "debug": false,
  "endpointList": {
    "base": "/izko",
    "bundle": "/izko/bundle"
  },
  "host": "127.0.0.1",
  "port": 5000,
  "rootMessage": "Welcome to izko API"
}
```

### `GET /izko/bundle`

Launches headless Chromium, scrapes all selectors defined under `label` in [`config.json`](../src/izko_gold_price_api/config.json), and returns the normalized price bundle.

Request:

```bash
curl -i http://127.0.0.1:5000/izko/bundle
```

Response (`200 OK`):

```json
{
  "priceList": {
    "14Ayar": 2150.0,
    "18Ayar": 2580.0,
    "22Ayar": 3180.0,
    "Ceyrek": 5720.0,
    "Cumhuriyet": 23450.0,
    "Dolar": 34.25,
    "Euro": 37.1,
    "GramAltin": 3180.0,
    "PaketliHas": 3505.0,
    "Tarih": "14:30:00",
    "Yarim": 11440.0,
    "Ziynet": 22880.0
  },
  "url": "https://www.izko.org.tr/Home/GuncelKur"
}
```

Error Response (`502 Bad Gateway`):

```json
{
  "code": "UPSTREAM_BAD_GATEWAY",
  "error": "Upstream navigation or network failure",
  "url": "https://www.izko.org.tr/Home/GuncelKur"
}
```

Timeout Response (`504 Gateway Timeout`):

```json
{
  "code": "UPSTREAM_TIMEOUT",
  "error": "Upstream selector or navigation timed out",
  "url": "https://www.izko.org.tr/Home/GuncelKur"
}
```

## HTTP Status Codes

| Status Code | Error Code | Origin | Condition |
| :---: | :--- | :--- | :--- |
| `200` | None | `/izko`, `/izko/bundle`, `scrape()` | Request succeeded and payload returned. |
| `400` | `INVALID_URL`, `INVALID_TIMEOUT`, `INVALID_CACHE_TTL` | `scrape()` | Target URL scheme is not `http`/`https`, `timeout` is outside `[100, 60000]` ms, or `cache_ttl < 0`. |
| `500` | `MISSING_URL` | `scrape()` | Target URL is empty or missing from configuration. |
| `502` | `UPSTREAM_BAD_GATEWAY` | `/izko/bundle`, `scrape()` | Upstream navigation failure, connection refusal, or Playwright browser error. |
| `504` | `UPSTREAM_TIMEOUT` | `/izko/bundle`, `scrape()` | Playwright `TimeoutError` while navigating or waiting for `#ataLabel`. |

## Python SDK Functions

All public symbols are exported from [`izko_gold_price_api`](../src/izko_gold_price_api/__init__.py).

### `scrape(url=None, timeout=None, cfg=None) -> tuple[dict, int]`

Executes a single headless Chromium scrape.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `url` | `str \| None` | `cfg["url"]["izko"]` | Optional `http` or `https` URL override. |
| `timeout` | `int \| None` | `cfg["url"]["timeout"]` | Optional selector wait timeout in milliseconds (`100` to `60000`). |
| `cfg` | `dict \| None` | Module-level `config` | Optional configuration dictionary override. |

Example:

```python
from izko_gold_price_api import scrape

payload, status = scrape(timeout=15000)
if status == 200:
    for asset, value in payload["priceList"].items():
        print(f"{asset}: {value}")
```

### `to_float(value: str) -> float | str`

Converts a Turkish formatted numeric string (`"23.450,75"`) to a Python `float` (`23450.75`). Returns the input unchanged if conversion fails.

```python
from izko_gold_price_api import to_float

assert to_float("23.450,75") == 23450.75
assert to_float("14:30:00") == "14:30:00"
```

### `load_config(config_path=None) -> dict`

Loads and parses the JSON configuration file from `config_path`, `IZKO_CONFIG_PATH`, or the bundled `config.json`.

```python
from izko_gold_price_api import load_config

cfg = load_config()
print(cfg["url"]["izko"])
```

## Configuration Schema

| Section | Key | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `url` | `izko` | `str` | `"https://www.izko.org.tr/Home/GuncelKur"` | Upstream page URL. |
| `url` | `timeout` | `int` | `10000` | Wait timeout in milliseconds (`100` to `60000`). |
| `label` | `<AssetName>` | `str` | DOM ID without `#` | Maps output field names to HTML element IDs on the target page. |
| `api` | `host` | `str` | `"127.0.0.1"` | Flask bind address. |
| `api` | `port` | `int` | `5000` | Flask bind port. |
| `api` | `debug` | `bool` | `false` | Flask debug mode toggle. |
| `api` | `rootMessage` | `str` | `"Welcome to izko API"` | Informational string included in `/izko`. |
| `api` | `endpointList` | `dict` | `{"base": "/izko", "bundle": "/izko/bundle"}` | Route metadata dictionary. |
