from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from urllib.error import HTTPError
from utils.provider import get_provider_available_instances_config_by_region_zone, get_provider_infos, get_provider_instances_pricing_by_region_zone, get_provider_available_instances, get_provider_available_instances_by_region_zone, get_providers
from utils.observability.otel import get_otel_tracer
from utils.observability.cid import get_current_cid
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method

router = APIRouter()

_span_prefix = "provider"
_counter = create_counter("provider_api", "Provider API counter")

@router.get("")
def get_all_providers():
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.ALL)):
        increment_counter(_counter, Method.GET, Action.ALL)
        return {
            'status': 'ok',
            'providers': get_providers()
        }

@router.get("/{provider}/region")
def get_provider_regions(provider: str):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.REGION)):
        increment_counter(_counter, Method.GET, Action.REGION)
        try:
            return {
                'status': 'ok',
                'regions': get_provider_infos(provider, "regions")
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.get("/{provider}/instance", status_code = status.HTTP_200_OK)
def get_instances_by_provider(provider: str):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.INSTANCE)):
        increment_counter(_counter, Method.GET, Action.INSTANCE)
        try:
            availability = get_provider_available_instances(provider)
            return {
                'status': 'ok',
                'availability': availability
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}")
def get_provider_instances_types( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.TYPE)):
        increment_counter(_counter, Method.GET, Action.TYPE)
        try:
            available_types = get_provider_available_instances_by_region_zone(provider, region, zone)
            return {
                'status': 'ok',
                'types': available_types
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ok',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}/pricing")
def get_provider_instances_pricing( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.PRICING)):
        increment_counter(_counter, Method.GET, Action.PRICING)
        try:
            instances_types_pricing = get_provider_instances_pricing_by_region_zone(provider, region, zone)
            return {
                'status': 'ok',
                'types': instances_types_pricing
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.get("/{provider}/instance/{region}/{zone}/config")
def get_provider_instances_config( provider: str, region: str, zone: str):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.CONFIG)):
        increment_counter(_counter, Method.GET, Action.CONFIG)
        try:
            instances_configs = get_provider_available_instances_config_by_region_zone(provider, region, zone)
            return {
                'status': 'ok',
                'instances': instances_configs
            }
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg,
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)
