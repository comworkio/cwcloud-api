import os
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "manifest"

@router.get("")
def get_manifest():
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        try:
            with open(os.environ['MANIFEST_FILE_PATH']) as manifest_file:
                manifest = json.load(manifest_file)
                return manifest
        except IOError as err:
            return JSONResponse(content = {"status": "error", "reason": err}, status_code = 500)
