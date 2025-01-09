ARG PYTHON_VERSION=3.9.16
ARG FLYWAYDB_VERSION=9.20-alpine

# Base image
FROM python:${PYTHON_VERSION} as api

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    MANIFEST_FILE_PATH=manifest.json \
    SLACK_TRIGGER="off" \
    SLACK_EMOJI=":comworkcloud:" \
    SLACK_CHANNEL="#cloud" \
    SLACK_USERNAME="comworkcloud" \
    LOG_LEVEL="INFO" \
    INVOICE_DAYS_DELTA=4 \
    INVOKE_SYNC_WAIT_TIME=1 \
    MAX_RETRY_INVOKE_SYNC=100 \
    LOOP_WAIT_TIME=10 \
    UVICORN_WORKERS=10 \
    API_MAX_RESULTS=100 \
    PATH="/root/.pulumi/bin:${PATH}" \
    TIMEOUT=60 \
    MONITOR_WAIT_TIME=300 \
    MONITORS_MAX_NUMBER=10 \
    WAIT_TIME=10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends wkhtmltopdf git && \
    curl -fsSL https://get.pulumi.com | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt

RUN find . -name '*.pyc' -type f -delete && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf *.tgz && \
    apt clean -y

# API image
COPY . /app/

EXPOSE 5000

CMD ["python", "src/app.py"]

# Scheduler image
FROM api as scheduler

CMD ["python", "src/scheduler.py"]

# Consumer image
FROM api as consumer

RUN mkdir -p /functions && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl golang-go jq gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" >> /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "src/consumer.py"]

# Unit tests image
FROM api AS unit_tests

WORKDIR /app/src

CMD ["python", "-m", "unittest", "discover", "-s", "./tests", "-p", "test_*.py", "-v"]

# Linter image
FROM api AS linter

WORKDIR /app/src

CMD ["ruff", "check", "--fix", "."]

# Scan
FROM api AS code_scanner

WORKDIR /app/src

RUN pip install bandit

CMD ["bandit", "-r", ".", "-f", "screen"]
