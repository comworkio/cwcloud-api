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
    UVICORN_WORKERS=10

WORKDIR /app

RUN apt update && \
    apt upgrade -y && \
    apt install -y wkhtmltopdf && \
    apt-get install -y git

RUN curl -fsSL https://get.pulumi.com | sh
ENV PATH="/root/.pulumi/bin:${PATH}"
ENV API_MAX_RESULTS=100

# FIX pulumi public bucket has been removed
# See this issue: https://github.com/pulumiverse/pulumi-scaleway/issues/117
ARG PULUMI_SCW_OLD_VERSION=0.1.8 \
    PULUMI_SCW_VERSION=1.7.0 \
    PULUMI_OVH_VERSION=0.0.4

RUN pulumi plugin install resource scaleway v${PULUMI_SCW_OLD_VERSION} --server https://pulumi-scw.s3.fr-par.scw.cloud/v${PULUMI_SCW_OLD_VERSION}/ && \
    pulumi plugin install resource scaleway v${PULUMI_SCW_VERSION} --server https://pulumi-scw.s3.fr-par.scw.cloud/v${PULUMI_SCW_VERSION}/ && \
    pulumi plugin install resource ovh v${PULUMI_OVH_VERSION} --server https://pulumi-ovh.s3.fr-par.scw.cloud/v${PULUMI_OVH_VERSION}/

COPY ./requirements.txt /app/requirements.txt

RUN find . -name '*.pyc' -type f -delete && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    curl -fsSL https://gitlab.comwork.io/oss/lbrlabs/-/raw/main/lbrlabs_ovh.tgz -o lbrlabs_ovh.tgz && \
    tar -xvzf lbrlabs_ovh.tgz && \
    curl -fsSL https://gitlab.comwork.io/oss/lbrlabs/-/raw/main/lbrlabs_pulumi_ovh.tgz -o lbrlabs_pulumi_ovh.tgz && \
    tar -xvzf lbrlabs_pulumi_ovh.tgz && \
    curl https://gitlab.comwork.io/oss/lbrlabs/-/raw/main/lbrlabs_pulumi_ovh-${PULUMI_OVH_VERSION}.dist-info.tgz -o lbrlabs_pulumi_ovh-${PULUMI_OVH_VERSION}.dist-info.tgz && \
    tar -xvzf lbrlabs_pulumi_ovh-${PULUMI_OVH_VERSION}.dist-info.tgz && \
    mv lbrlabs_* /usr/local/lib/python3.9/site-packages/ && \
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
