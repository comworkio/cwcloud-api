from urllib.error import HTTPError
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Query

from database.postgres_db import get_db
from middleware.auth_guard import get_current_active_user
from schemas.User import UserSchema

from utils.common import is_false
from utils.date import parse_date
from utils.consumption import generate_instance_consumption, generate_user_consumptions, getInstanceConsumptionsByDate
from utils.consumption import getUserConsumptionsByDate
from utils.observability.otel import get_otel_tracer
from utils.observability.traces import span_format
from utils.observability.counter import create_counter, increment_counter
from utils.observability.enums import Action, Method
from utils.observability.cid import get_current_cid

router = APIRouter()

_span_prefix = "consumption"
_counter = create_counter("consumption_api", "Consumption API counter")

@router.get("")
def get_consumption(current_user: Annotated[UserSchema, Depends(get_current_active_user)], consumption_from: str = Query(None, alias = "from"), consumption_to: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.USER)):
        increment_counter(_counter, Method.GET, Action.USER)
        try:
            from_date = parse_date(consumption_from)
            from_date_iso = from_date["value"]
            to_date = parse_date(consumption_to)
            to_date_iso = to_date["value"]

            if is_false(from_date["status"]):
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': "The date is not correct: {}".format(from_date_iso), 
                    'i18n_code': 'bad_date_aaaammdd',
                    'cid': get_current_cid()
                }, status_code = 400)

            if is_false(to_date["status"]):
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'The date is not correct: {}'.format(to_date_iso), 
                    'i18n_code': 'bad_date_aaaammdd',
                    'cid': get_current_cid()
                }, status_code = 400)

            unregistred_consumptions = getUserConsumptionsByDate(from_date, to_date, current_user.id, db)
            current_consumptions = generate_user_consumptions(current_user.id, from_date_iso, to_date_iso, db)
            current_consumptions.extend(unregistred_consumptions)
            consumptions_json = []
            for consumption in current_consumptions:
                consumptions_json.append({**consumption, "instance_name": consumption["instance"]["name"]})

            return JSONResponse(content = consumptions_json, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg, 
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)

@router.get("/{instance_id}")
def get_consumption_by_instance_id(current_user: Annotated[UserSchema, Depends(get_current_active_user)], instance_id: str, consumption_from: str = Query(None, alias = "from"), consumption_to: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span(span_format(_span_prefix, Method.GET, Action.INSTANCE)):
        increment_counter(_counter, Method.GET, Action.INSTANCE)
        try:
            from_date = parse_date(consumption_from)
            from_date_iso = from_date["value"]
            to_date = parse_date(consumption_to)
            to_date_iso = to_date["value"]

            if is_false(from_date["status"]):
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': "The date is not correct: {}".format(from_date_iso), 
                    'i18n_code': 'bad_date_aaaammdd',
                    'cid': get_current_cid()
                }, status_code = 400)

            if is_false(to_date["status"]):
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': "The date is not correct: {}".format(to_date_iso), 
                    'i18n_code': 'bad_date_aaaammdd',
                    'cid': get_current_cid()
                }, status_code = 400)

            from entities.Instance import Instance
            target_instance = Instance.getUserInstance(current_user.id, instance_id, db)
            if not target_instance:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'Instance not found', 
                    'i18n_code': '104',
                    'cid': get_current_cid()
                }, status_code = 404)
            consumptions = []
            if to_date and from_date:
                consumptions.extend(getInstanceConsumptionsByDate(target_instance.id, from_date, to_date, db))
                recent_instance_consumption = generate_instance_consumption(target_instance.user_id, target_instance, from_date_iso, to_date_iso, False, db)
                if recent_instance_consumption:
                    consumptions.append(recent_instance_consumption)
                return JSONResponse(content = consumptions, status_code = 200)
            else:
                return JSONResponse(content = {
                    'status': 'ko',
                    'error': 'please provide from and to dates arguments',
                    'cid': get_current_cid()
                }, status_code = 400)

        except HTTPError as e:
            return JSONResponse(content = {
                'status': 'ko',
                'error': e.msg, 
                'i18n_code': e.headers['i18n_code'],
                'cid': get_current_cid()
            }, status_code = e.code)
