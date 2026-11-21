FROM python:3.15-slim
LABEL authors="atacan"

WORKDIR /app

# Install Playwright system dependencies as root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg unzip curl ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy package files and install
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir . \
    && playwright install-deps chromium \
    && chown -R appuser:appuser /app

# Drop root privileges and install Chromium binary under appuser
USER appuser
RUN playwright install chromium

EXPOSE 5000

CMD ["izko-gold-price-api", "serve", "--host", "0.0.0.0", "--port", "5000", "--no-debug"]
