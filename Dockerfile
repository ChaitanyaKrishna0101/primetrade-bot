# ─────────────────────────────────────────────────────────────────────────────
# PrimeTrade Bot — Dockerfile
# Multi-stage build: lean final image, non-root user, no dev deps in prod.
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install only what's needed to compile deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="PrimeTrade Bot"
LABEL org.opencontainers.image.description="Binance Futures Testnet trading bot with AI analysis"
LABEL org.opencontainers.image.source="https://github.com/your-username/primetrade-bot"

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy source code
COPY --chown=appuser:appgroup . .

# Create logs directory with correct permissions
RUN mkdir -p logs && chown appuser:appgroup logs

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE 7860

# Health check — verifies the app is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:7860').raise_for_status()" || exit 1

# Default command: launch Gradio web UI
# Override with `docker run ... python cli.py order ...` for CLI usage
CMD ["python", "app.py"]
