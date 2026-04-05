FROM python:3.13-slim

# System dependencies for scipy/numpy wheel compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Apply pkg_resources patch for Python 3.13
COPY app/patch.py .
RUN python patch.py && rm patch.py

# Copy application code
COPY app/ ./app/

# Create results directory for optional volume mount
RUN mkdir -p /app/results

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
