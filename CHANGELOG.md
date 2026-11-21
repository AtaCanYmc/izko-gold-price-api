# Changelog

All notable changes to `izko-gold-price-api` are documented in this file.

## [0.1.0](https://github.com/AtaCanYmc/izko-gold-price-api/releases/tag/v0.1.0) (2026-11-21)

### Features

* Headless Chromium scraping of live gold and currency rates from `izko.org.tr/Home/GuncelKur` using Playwright.
* Flask REST API endpoints `/izko` and `/izko/bundle`.
* Turkish formatted decimal normalization via `to_float()`.
* Standard `src/izko_gold_price_api` PyPI package structure and `izko-gold-price-api` CLI entry point.
