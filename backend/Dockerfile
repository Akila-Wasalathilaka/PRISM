FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install . --no-cache-dir

# Copy application code
COPY prism/ prism/

# Create data directory for persistent storage
RUN mkdir -p /app/data
ENV PRISM_DATA_DIR=/app/data

EXPOSE 8000

CMD ["uvicorn", "prism.main:app", "--host", "0.0.0.0", "--port", "8000"]
