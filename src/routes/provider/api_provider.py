from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from urllib.error import HTTPError
from utils.provider import get_provider_available_instances_config_by_region_zone, get_provider_infos, get_provider_instances_pricing_by_region_zone, get_provider_available_instances, get_provider_available_instances_by_region_zone, get_providers
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "provider"

@router.get("")
def get_all_providers():
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        return {
            "status": "ok",
            "providers": get_providers()
        }

@router.get("/{provider}/region")
def get_provider_regions(provider: str):
    with get_otel_tracer().start_as_current_span("{}-regions".format(_span_prefix)):
        try:
            return {
            "status": "ok",
            "regions": get_provider_infos(provider, "regions")
        }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{provider}/instance", status_code = status.HTTP_200_OK)
def get_instances_by_provider(provider: str):
    with get_otel_tracer().start_as_current_span("{}-instances".format(_span_prefix)):
        try:
            availability = get_provider_available_instances(provider)
            return {
            "status": "ok",
            "availability": availability
            }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}")
def get_provider_instances( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span("{}-instances-byzone".format(_span_prefix)):
        try:
            available_types = get_provider_available_instances_by_region_zone(provider, region, zone)
            return {
            "status": "ok",
            "types": available_types
            }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}/pricing")
def get_provider_instances_pricing( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span("{}-instances-pricing".format(_span_prefix)):
        try:
            instances_types_pricing = get_provider_instances_pricing_by_region_zone(provider, region, zone)
            return {
                "status": "ok",
                "types": instances_types_pricing
            }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}/config")
def get_provider_instances_config( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span("{}-instances-config".format(_span_prefix)):
        try:
            instances_configs = get_provider_available_instances_config_by_region_zone(provider, region, zone)
            return {
                "status": "ok",
                "instances": instances_configs
            }
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
