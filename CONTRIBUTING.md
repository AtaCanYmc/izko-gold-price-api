# Contributing to izko-gold-price-api

Contributions must preserve simplicity, deterministic behavior, and compatibility with the `config.json` schema.

## Development Setup

```bash
git clone https://github.com/AtaCanYmc/izko-gold-price-api.git
cd izko-gold-price-api
python3 -m venv venv
source venv/bin/activate
pip install -e .
playwright install chromium
```

## Commit Message Format

This repository follows [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New endpoint, selector support, or configuration capability
- `fix`: Bug fix in scraping, number parsing, or HTTP status handling
- `docs`: Documentation and governance updates
- `refactor`: Internal code restructuring without behavior change
- `test`: Verification scripts or test cases
- `chore`: Dependency updates, packaging adjustments, or CI maintenance

## Pre-Submission Verification

Run these checks locally before opening a pull request:

```bash
# 1. Check Python compilation
python -m py_compile src/izko_gold_price_api/__init__.py src/izko_gold_price_api/app.py src/izko_gold_price_api/scrape.py

# 2. Validate config.json structure
python -c "import json; c = json.load(open('src/izko_gold_price_api/config.json')); assert 'url' in c and 'label' in c and 'api' in c"

# 3. Verify Turkish decimal parsing (with virtualenv active)
python -c "from izko_gold_price_api import to_float; assert to_float('3.180,50') == 3180.5"
```

## Pull Request Checklist

1. Branch from `main` using a descriptive name such as `fix/selector-timeout` or `feat/ttl-cache`.
2. Keep changes focused on a single concern.
3. Update `README.md` and `src/izko_gold_price_api/config.json` if any route or configuration key changes.
4. Complete the pull request template with reproduction and verification commands.
