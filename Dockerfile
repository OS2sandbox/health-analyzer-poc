FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

# Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser \
  && mkdir -p output \
  && chown -R appuser:appuser output

USER appuser

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

ENTRYPOINT ["python", "./src/metrics_check.py"]
