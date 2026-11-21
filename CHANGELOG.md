# Changelog

All notable changes to `izko-gold-price-api` are documented in this file.

## [0.2.1](https://github.com/AtaCanYmc/izko-gold-price-api/compare/v0.2.0...v0.2.1) (2026-11-21)


### Documentation

* add Homebrew tap badge and install command ([39da062](https://github.com/AtaCanYmc/izko-gold-price-api/commit/39da062c0c8e83393eb2f64a3635fb23ba57f1fe))
* add square SVG logo and PyPI release badge ([cce6148](https://github.com/AtaCanYmc/izko-gold-price-api/commit/cce61482cc0aaf0fefa68112a0b90698bb53f1f3))

## [0.1.1](https://github.com/AtaCanYmc/izko-gold-price-api/compare/v0.1.0...v0.1.1) (2026-11-21)


### Features

* **cli:** add argparse CLI module with serve, scrape, and config subcommands ([c97018d](https://github.com/AtaCanYmc/izko-gold-price-api/commit/c97018dca6eb389c09c465825ec326650f4d7cac))
* **mcp:** add stdio MCP server module with tools and resources ([d5db579](https://github.com/AtaCanYmc/izko-gold-price-api/commit/d5db57978f25697448ae29246c516fab3a177a5c))
* **scraper:** reuse persistent Playwright context, add TTL cache, structured 502/504 errors, and env overrides ([69a9319](https://github.com/AtaCanYmc/izko-gold-price-api/commit/69a931945a84ba70328cf7001984c4d0fe7c7912))


### Bug Fixes

* **pkg:** export Flask app instance directly in __init__.py instead of submodule via __getattr__ ([a62757c](https://github.com/AtaCanYmc/izko-gold-price-api/commit/a62757c18aa168f232c98ecd813d79d3dd2acb62))
* **security:** disable Flask debug by default, enforce HTTP(S) URLs and timeout bounds, drop container root ([3c6c59d](https://github.com/AtaCanYmc/izko-gold-price-api/commit/3c6c59dbd9832c75170c3ca352f9c449f8eee8db))


### Code Refactoring

* **packaging:** restructure into src/izko_gold_price_api for PyPI distribution ([4930513](https://github.com/AtaCanYmc/izko-gold-price-api/commit/4930513dc4165ff1fa03a56fef9e025a6c8d7d88))


### Documentation

* add technical documentation suite under docs/ ([6c91054](https://github.com/AtaCanYmc/izko-gold-price-api/commit/6c91054dd435df603fc895d988b19e06625ab433))
* **i18n:** add Turkish README.tr.md and Makefile automation ([9de6141](https://github.com/AtaCanYmc/izko-gold-price-api/commit/9de6141c4e074e30f1c82ab7398efb2876292236))
* scaffold production documentation, governance, and CI workflows ([2315f7c](https://github.com/AtaCanYmc/izko-gold-price-api/commit/2315f7c7091c73855185212fe13efc79a802429d))

## [0.1.0](https://github.com/AtaCanYmc/izko-gold-price-api/releases/tag/v0.1.0) (2026-11-21)

### Features

* Headless Chromium scraping of live gold and currency rates from `izko.org.tr/Home/GuncelKur` using Playwright.
* Flask REST API endpoints `/izko` and `/izko/bundle`.
* Turkish formatted decimal normalization via `to_float()`.
* Standard `src/izko_gold_price_api` PyPI package structure and `izko-gold-price-api` CLI entry point.
