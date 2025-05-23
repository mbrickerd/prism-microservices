FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY producer/pyproject.toml producer/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ./producer

COPY producer/ /app/producer/

FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/producer ./producer
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -s /bin/bash -m appuser

RUN mkdir -p /app/data /tmp/app_temp && \
    chown -R appuser:appuser /app /tmp/app_temp

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports for health checks and metrics
EXPOSE 8080 8000

USER 1001

ENV TMPDIR=/tmp/app_temp

CMD ["python", "-m", "producer.app"]