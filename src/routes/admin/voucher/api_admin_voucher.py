import json
import datetime

from urllib.error import HTTPError
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends, APIRouter, status
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Voucher import VoucherAdminSchema

from utils.common import is_duration_valid, is_not_empty
from utils.observability.otel import get_otel_tracer
from utils.encoder import AlchemyEncoder

router = APIRouter()

_span_prefix = "adm-voucher"

@router.post("", status_code = status.HTTP_201_CREATED)
def create_voucher(current_user: Annotated[UserSchema, Depends(admin_required)], payload: VoucherAdminSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        code = payload.code
        email = payload.email
        validity = payload.validity
        price = payload.price
        user_id = 0
        if is_not_empty(email):
            from entities.User import User
            exist_user = User.getUserByEmail(email, db)
            if not exist_user:
                return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)
            user_id = exist_user.id

        from entities.Voucher import Voucher
        exist_voucher = Voucher.getByCode(code, db)
        if exist_voucher:
            return JSONResponse(content = {"error": "voucher already exists"}, status_code = 400)
        new_voucher = Voucher()
        new_voucher.user_id = user_id
        new_voucher.validity = validity
        new_voucher.price = price
        new_voucher.code = code
        new_voucher.save(db)
        return JSONResponse(content = {"message": "voucher sucessfully added"}, status_code = 200)

@router.get("", status_code = status.HTTP_200_OK)
def get_all_vouchers(current_user: Annotated[UserSchema, Depends(admin_required)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get-all".format(_span_prefix)):
        from entities.Voucher import Voucher
        from entities.RegisteredVoucher import RegisteredVoucher
        vouchers = Voucher.getAll(db)
        registeredVouchers = RegisteredVoucher.getAll(db)
        vouchersJson = json.loads(json.dumps(vouchers, cls = AlchemyEncoder))
        activeVouchers = []
        oldVouchers = []
        for voucher in vouchersJson:
            if voucher["user_id"] == 0:
                activeVouchers.append({**voucher, "credit": voucher["price"]});
                continue;

            user_registered_voucher = [rv for rv in registeredVouchers if rv.user_id == voucher["user_id"] and rv.voucher_id == voucher["id"] ]
            if len(user_registered_voucher)>0:
                registeredVoucher = user_registered_voucher[0]
                if "validity" in voucher and is_duration_valid(voucher['validity']):
                    created_registered_voucher  = datetime.datetime.fromisoformat(registeredVoucher.created_at)
                    validity_date = created_registered_voucher + datetime.timedelta(days = voucher["validity"])
                    now_date = datetime.datetime.now()
                    if not now_date >= validity_date:
                        if registeredVoucher.credit > 0:
                            activeVouchers.append({**voucher, "credit": registeredVoucher.credit})
                        else:
                            oldVouchers.append({**voucher, "credit": registeredVoucher.credit})
                    else:
                        oldVouchers.append({**voucher, "credit": 0})
                else:
                    if registeredVoucher.credit > 0:
                        activeVouchers.append({**voucher, "credit": registeredVoucher.credit})
                    else:
                        oldVouchers.append({**voucher, "credit": registeredVoucher.credit})
            else:
                activeVouchers.append({**voucher, "credit": voucher["price"]});

        return JSONResponse(content = {"activeVouchers": activeVouchers, "oldVouchers": oldVouchers}, status_code = 200)

@router.delete("/{voucher_id}")
def delete_voucher_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], voucher_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-delete".format(_span_prefix)):
        try:
            from entities.Voucher import Voucher
            voucher = Voucher.getById(voucher_id, db)
            if not voucher:
                return JSONResponse(content = {"error": "voucher not found"}, status_code = 404)
            Voucher.deleteOne(voucher_id, db)
            return JSONResponse(content = {"message" : "voucher successfully deleted"}, status_code = 200)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)

@router.get("/{voucher_id}", status_code = status.HTTP_200_OK)
def get_voucher_by_id(current_user: Annotated[UserSchema, Depends(admin_required)], voucher_id: str, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        from entities.RegisteredVoucher import RegisteredVoucher
        from entities.Voucher import Voucher
        voucher = Voucher.getById(voucher_id, db)
        dumpedVoucher = json.loads(json.dumps(voucher, cls = AlchemyEncoder))
        if voucher.user_id and not voucher.user_id == 0:
            user_registered_vouchers = RegisteredVoucher.getUserRegisteredVouchers(voucher.user_id, db)
            registeredVouchers = [reg_v for reg_v in user_registered_vouchers if reg_v.voucher_id == voucher.id]
            if not len(registeredVouchers) > 0:
                return JSONResponse(content = {**dumpedVoucher, "credit": voucher.price}, status_code = 200)
            registeredVoucher = registeredVouchers[0]
            if voucher.validity != -1:
                created_registered_voucher  = datetime.datetime.fromisoformat(registeredVoucher.created_at)
                validity_date = created_registered_voucher + datetime.timedelta(days = voucher.validity)
                now_date = datetime.datetime.now()
                if not now_date >= validity_date:
                    return JSONResponse(content = {**dumpedVoucher, "credit": registeredVoucher.credit}, status_code = 200)
                else:
                    return JSONResponse(content = {**dumpedVoucher, "credit": 0}, status_code = 200)
            else:
                return JSONResponse(content = {**dumpedVoucher, "credit": registeredVoucher.credit}, status_code = 200)
        else:
            return JSONResponse(content = dumpedVoucher, status_code = 200)
