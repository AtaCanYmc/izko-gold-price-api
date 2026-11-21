# Security Policy

## Supported Versions

Only the latest commit on the `main` branch receives security updates.

| Version / Branch | Supported |
| :--- | :---: |
| `main` | Yes |
| Older commits | No |

## Reporting a Vulnerability

Do not open a public GitHub issue for security vulnerabilities.

1. Use [GitHub Private Vulnerability Reporting](https://github.com/AtaCanYmc/izko-gold-price-api/security/advisories/new) or email `atacanymc@gmail.com` with the subject line `[SECURITY] izko-gold-price-api`.
2. Include steps to reproduce, affected files (`app.py`, `scrape.py`, `Dockerfile`), and potential impact.
3. Initial acknowledgment is provided within 48 hours of receipt.
4. Validated fixes are patched on `main` and disclosed after remediation.

## Operational Security Notes

- `config.json` ships with `"debug": false` by default to prevent Werkzeug interactive debugger exposure.
- `scrape()` enforces `http`/`https` URL schemes, bounds selector wait timeouts between `100` and `60000` ms, and closes headless Chromium inside a `finally` block.
- `Dockerfile` runs the service under an unprivileged `appuser` account with `--no-debug`.
- Run production containers behind a reverse proxy with rate limiting to prevent upstream scraping abuse and browser memory exhaustion.
