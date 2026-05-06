FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY app ./app

HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=15s \
  CMD curl -f http://localhost:${SERVICE_PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8000}"]
