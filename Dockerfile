FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Update available Debian security packages
RUN apt-get update && \
#    apt-get upgrade -y && \
    apt-get install -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    # Force upgrade hidden package tools to fix CVE-2026-24049 and CVE-2026-23949
RUN python -m pip install --no-cache-dir --upgrade pip

# Install Python dependencies once
COPY requirements.txt  .

# 2. Install your dependencies AND force override the vulnerable packages at the exact same time
RUN python -m pip install --no-cache-dir  -r requirements.txt  

# Copy application
COPY app/ ./app/

# Create non-root application user
RUN useradd --create-home --shell /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"