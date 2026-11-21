.PHONY: help install run verify build check-dist publish docker-build docker-run clean

PYTHON ?= python3
IMAGE_NAME ?= izko-gold-price-api
CONTAINER_NAME ?= izko-api
PORT ?= 5000

help: ## Kullanilabilir hedefleri listeler / List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Paketi duzenlenebilir modda ve Chromium tarayicisini kurar / Install package in editable mode with Chromium
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m playwright install chromium

run: ## Flask REST API sunucusunu baslatir / Start the Flask REST API server
	izko-gold-price-api

verify: ## Sozdizimi, yapilandirma ve dokumantasyon baglantilarini dogrular / Verify syntax, config, and doc links
	$(PYTHON) -m py_compile src/izko_gold_price_api/__init__.py src/izko_gold_price_api/app.py src/izko_gold_price_api/scrape.py
	$(PYTHON) -c 'import json, re, glob, os; \
		cfg = json.load(open("src/izko_gold_price_api/config.json", encoding="utf-8")); \
		assert "url" in cfg and "label" in cfg and "api" in cfg; \
		[(_ for _ in ()).throw(AssertionError(f"Broken link in {f}: {l}")) \
		for f in glob.glob("**/*.md", recursive=True) if not f.startswith("venv/") \
		for l in re.findall(r"\[.*?\]\((?!https?://|mailto:)(.*?)(?:#.*)?\)", re.sub(r"`[^`]*`", "", re.sub(r"```[\s\S]*?```", "", open(f, encoding="utf-8").read()))) \
		if l.strip() and not l.strip().startswith("#") and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), l.strip())))]'
	@echo "Verification passed."

build: clean ## PyPI sdist ve wheel paketlerini olusturur / Build PyPI sdist and wheel artifacts
	$(PYTHON) -m pip install --upgrade build twine
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

publish: build ## Paketleri PyPI uzerine yukler / Upload distributions to PyPI
	$(PYTHON) -m twine upload dist/*

docker-build: ## Docker imajini derler / Build Docker image
	docker build -t $(IMAGE_NAME) .

docker-run: ## Docker konteynerini arka planda baslatir / Run Docker container in background
	docker run -d -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

clean: ## Derleme ve onbellek artefaktlarini temizler / Remove build and cache artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -delete
