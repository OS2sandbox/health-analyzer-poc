# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy config directory
COPY config/ ./config/

# Copy the main script
COPY src/metrics_check.py .

# Create output directory
RUN mkdir -p output

# Set environment variables with defaults
ENV CONFIG_FILE=config/config.yaml
ENV OUTPUT_DIR=output

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Set entrypoint
ENTRYPOINT ["python", "metrics_check.py"]
