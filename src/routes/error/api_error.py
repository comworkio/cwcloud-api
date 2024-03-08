from fastapi import APIRouter

from exceptions.CwHTTPException import CwHTTPException

from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "error"

@router.get("/400")
def generate_functional_ex():
    with get_otel_tracer().start_as_current_span("{}-func".format(_span_prefix)):
        raise CwHTTPException(message = {"error": "functional error test", "i18n_code": "functional_error"}, status_code = 400)

@router.get("/500")
def generate_technical_ex():
    with get_otel_tracer().start_as_current_span("{}-tech".format(_span_prefix)):
        raise Exception("technical error test")
