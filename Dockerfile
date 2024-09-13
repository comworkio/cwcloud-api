ARG PYTHON_VERSION=3.9.16
ARG FLYWAYDB_VERSION=9.20-alpine

FROM python:${PYTHON_VERSION} as api

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    MANIFEST_FILE_PATH=manifest.json \
    SLACK_TRIGGER="off" \
    SLACK_EMOJI=":comworkcloud:" \
    SLACK_CHANNEL="#cloud" \
    SLACK_USERNAME="comworkcloud" \
    LOG_LEVEL="INFO" \
    INVOICE_DAYS_DELTA=4 \
    LISTEN_ADDR="0.0.0.0" \
    LISTEN_PORT=5000 \
    INVOKE_SYNC_WAIT_TIME=1 \
    MAX_RETRY_INVOKE_SYNC=100 \
    LOOP_WAIT_TIME=10 \
    UVICORN_WORKERS=10 \
    API_MAX_RESULTS=100

WORKDIR /app

RUN apt update && \
    apt upgrade -y && \
    apt install -y wkhtmltopdf && \
    apt-get install -y git && \
    curl -fsSL https://get.pulumi.com | sh

ENV PATH="/root/.pulumi/bin:${PATH}"

COPY ./requirements.txt /app/requirements.txt

RUN find . -name '*.pyc' -type f -delete && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf *.tgz && \
    apt clean -y

COPY . /app/

EXPOSE 5000

CMD ["python", "src/app.py"]

FROM api as scheduler


CMD ["python", "src/scheduler.py"]

FROM api as consumer

RUN mkdir -p /functions && \
    apt update -y && \
    apt install -y ca-certificates curl golang-go jq gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" >> /etc/apt/sources.list.d/nodesource.list && \
    apt update -y && \
    apt install -y nodejs && \
    apt clean -y

CMD ["python", "src/consumer.py"]

FROM api AS unit_tests

WORKDIR /app/src

CMD ["python", "-m", "unittest", "discover", "-s", "./tests", "-p", "test_*.py", "-v"]

FROM api AS linter

WORKDIR /app/src

CMD ["ruff", "check", "--fix", "."]
