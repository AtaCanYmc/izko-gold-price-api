# Roadmap

Technical milestones for `izko-gold-price-api`, organized by target release stage.

## v0.1.0: Baseline Service (Current)

- [x] Headless Chromium scraping of `izko.org.tr/Home/GuncelKur` using Playwright.
- [x] Turkish formatted number normalization (`to_float`) in `scrape.py`.
- [x] Flask REST endpoints `/izko` and `/izko/bundle`.
- [x] Externalized DOM selector and server configuration in `config.json`.
- [x] Containerized runtime via `Dockerfile`.

## v0.2.0: Reliability and Caching

- [ ] Reuse a single persistent Playwright browser context across requests instead of launching Chromium per call.
- [ ] Add configurable in-memory TTL response caching to reduce upstream requests and latency.
- [ ] Catch Playwright `TimeoutError` and network failures in `scrape.py` and return structured HTTP 502/504 JSON responses.

## v0.3.0: Production Hardening

- [ ] Add WSGI server entrypoint (`gunicorn`) for production container deployments.
- [ ] Support environment variable overrides (`IZKO_HOST`, `IZKO_PORT`, `IZKO_DEBUG`, `IZKO_TIMEOUT`).
- [ ] Add unit and mocked DOM integration tests for `scrape.py` and `app.py`.
