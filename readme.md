# İzko Gold Price API Scraper

A lightweight Python-based API that scrapes real-time gold and currency prices from the İzmir Jewelers Association website. Built using **Playwright** for dynamic content rendering and **Flask** to expose the data as a RESTful API.

## Features

- Scrapes current gold prices for multiple types:
  - 22K, 18K, 14K
  - Gram Gold
  - Cumhuriyet, Çeyrek, Yarım, Ziynet, Paketli Has
- Retrieves exchange rates for:
  - USD
  - EUR
- Returns data in a clean JSON format suitable for front-end consumption or automation workflows.
- Supports external access via Flask server (`host` configurable).
- Efficient browser handling with Playwright, including headless operation and optional caching.

## Installation

```bash
git clone https://github.com/AtaCanYmc/izko-gold-price-api
cd izko-gold-price-api
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
playwright install         # download necessary browsers
