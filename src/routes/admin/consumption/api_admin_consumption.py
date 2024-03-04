from urllib.error import HTTPError
from utils.common import is_false
from utils.date import parse_date
from utils.consumption import generate_instance_consumption, generate_user_consumptions
from utils.consumption import getUserConsumptionsByDate, getInstanceConsumptionsByDate
from fastapi import Depends, APIRouter, Query
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from middleware.auth_guard import admin_required
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/{user_id}")
def get_all_consumptions_by_user_id(current_user: Annotated[UserSchema, Depends(admin_required)], user_id: str, consumption_from: str = Query(None, alias = "from"), consumption_to: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    try:
        from_date = consumption_from
        to_date = consumption_to

        from entities.User import User
        target_user = User.getUserById(user_id, db)
        if not target_user:
            return JSONResponse(content = {"error": "instance not found", "i18n_code": "104"}, status_code = 404)

        consumptions = getUserConsumptionsByDate(from_date, to_date, user_id, db)
        all_consumptions = generate_user_consumptions(user_id, from_date, to_date, db)
        all_consumptions.extend(consumptions)
        return JSONResponse(content = all_consumptions, status_code = 200)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{instance_id}")
def get_all_consumptions_by_instance_id(current_user: Annotated[UserSchema, Depends(admin_required)], instance_id: str, consumption_from: str = Query(None, alias = "from"), consumption_to: str = Query(None, alias = "to"), db: Session = Depends(get_db)):
    try:
        to_date = parse_date(consumption_to)
        if is_false(to_date["status"]):
            return JSONResponse(content = {"error": "The date is not correct :{}".format(to_date["value"]), "i18n_code": "bad_date_aaaammdd"}, status_code = 400)

        from_date = parse_date(consumption_from)
        if is_false(from_date["status"]):
            return JSONResponse(content = {"error": "The date is not correct :{}".format(from_date["value"]), "i18n_code": "bad_date_aaaammdd"}, status_code = 400)

        from entities.Instance import Instance
        target_instance = Instance.findInstanceById(instance_id, db)
        if not target_instance:
            return JSONResponse(content = {"error": "instance not found", "i18n_code": "104"}, status_code = 404)

        consumptions = []
        if to_date and from_date:
            from_date_iso = from_date["value"]
            to_date_iso = to_date["value"]
            consumptions.extend(getInstanceConsumptionsByDate(target_instance.id, from_date, to_date, db))
            recent_instance_consumption = generate_instance_consumption(target_instance.user_id, target_instance, from_date_iso, to_date_iso, False, db)
            if recent_instance_consumption:
                consumptions.append(recent_instance_consumption)
            return JSONResponse(content = consumptions, status_code = 200)
        else:
            return JSONResponse(content = {"error": "please provide from and to dates arguments"})

    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
