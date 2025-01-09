import os
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from utils.observability.cid import get_current_cid
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Method

router = APIRouter()

_span_prefix = "manifest"
_counter = create_counter("manifest_api", "Manifest API counter")

MANIFEST_FILE_PATH = os.getenv('MANIFEST_FILE_PATH', 'manifest.json')

@router.get("")
def get_manifest():
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET)):
        increment_counter(_counter, Method.GET)
        try:
            with open(MANIFEST_FILE_PATH) as manifest_file:
                manifest = json.load(manifest_file)
                return manifest
        except IOError as err:
            return JSONResponse(content = {
                'status': 'ko',
                'error': err,
                'cid': get_current_cid()
            }, status_code = 500)
