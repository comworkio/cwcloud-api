import os
import logging

from uuid import uuid4
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from prometheus_fastapi_instrumentator import Instrumentator
from asgi_correlation_id import CorrelationIdMiddleware

from restful_resources import import_resources
from exceptions.CwHTTPException import CwHTTPException
from database.postgres_db import dbEngine
from database.postgres_db import Base

from utils.common import is_true
from utils.logger import log_msg
from utils.cid import get_current_cid
from utils.observability.metrics import metrics
from utils.observability.otel import init_otel_metrics, init_otel_tracer

logger = logging.getLogger('git')
logger.setLevel(logging.INFO)
logger = logging.getLogger('kubernetes')
logger.setLevel(logging.INFO)

log_msg("INFO", "[main] the application is starting with version = {}".format(os.environ['APP_VERSION']))
Base.metadata.create_all(bind = dbEngine)

app = FastAPI(
    docs_url = "/",
    title = "Comwork Cloud API",
    version = os.environ['APP_VERSION'],
    description = "Official Comwork Cloud API Swagger documentation."
)

app.add_middleware(
    CorrelationIdMiddleware,
    header_name = 'x-comwork-cid',
    generator = lambda: "{}".format(uuid4())
)

if os.getenv('APP_ENV') == 'local' or is_true(os.getenv('ENABLE_CORS_ALLOW_ALL')):
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"]
    )

instrumentator = Instrumentator()

init_otel_tracer()
init_otel_metrics()
metrics()

instrumentator.instrument(app, metric_namespace='cwcloudapi', metric_subsystem='cwcloudapi')
instrumentator.expose(app, endpoint='/v1/metrics')
instrumentator.expose(app, endpoint='/metrics')

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    headers = {'x-comwork-cid': get_current_cid()}

    if isinstance(exc, CwHTTPException):
        return JSONResponse(content = exc.message, status_code = exc.status_code, headers = headers)
    return await http_exception_handler(request, HTTPException(500, 'Internal server error', headers = headers))

import_resources(app)
