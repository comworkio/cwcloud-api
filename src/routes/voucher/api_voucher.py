import json
import datetime

from fastapi import Depends, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from schemas.User import UserSchema
from schemas.Voucher import VoucherSchema
from middleware.auth_guard import get_current_active_user
from database.postgres_db import get_db

from utils.common import is_duration_valid
from utils.encoder import AlchemyEncoder
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "voucher"

@router.post("")
def add_voucher(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: VoucherSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        from entities.Voucher import Voucher
        voucher = Voucher.getByCode(payload.code, db)
        if not voucher:
            return JSONResponse(content = {"error": "voucher not found", "i18n_code": "1204"}, status_code = 404)
        if voucher.user_id != current_user.id and voucher.user_id == 0:
            return JSONResponse(content = {"error": "voucher not found", "i18n_code": "1204"}, status_code = 404)

        from entities.RegisteredVoucher import RegisteredVoucher
        exist_registered_voucher = RegisteredVoucher.getUserRegisteredVoucher(current_user.id, voucher.id, db)
        if exist_registered_voucher:
            return JSONResponse(content = {"error": "voucher not found", "i18n_code": "1204"}, status_code = 404)

        registeredVoucher = RegisteredVoucher()
        registeredVoucher.user_id = current_user.id
        registeredVoucher.voucher_id = voucher.id
        registeredVoucher.credit = voucher.price
        registeredVoucher.save(db)
        from entities.User import User
        User.updateUserBillableStatus(current_user.id, True, db)
        voucherJson = json.loads(json.dumps(voucher, cls = AlchemyEncoder))
        voucherJson["id"] = registeredVoucher.id
        return JSONResponse(content = voucherJson, status_code = 201)

@router.get("")
def get(current_user: Annotated[UserSchema, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-get".format(_span_prefix)):
        from entities.RegisteredVoucher import RegisteredVoucher
        from entities.Voucher import Voucher
        user_registered_vouchers = RegisteredVoucher.getUserRegisteredVouchers(current_user.id, db)
        vouchersIds = [registered_voucher.voucher_id for registered_voucher in user_registered_vouchers]
        user_vouchers = Voucher.findVouchers(vouchersIds, db)
        vouchersJson = []
        for voucher in user_vouchers:
            registeredVoucher = [reg_v for reg_v in user_registered_vouchers if reg_v.voucher_id == voucher.id][0]
            if is_duration_valid(voucher.validity):
                created_registered_voucher = datetime.datetime.fromisoformat(registeredVoucher.created_at)
                validity_date = created_registered_voucher + datetime.timedelta(days = voucher.validity)
                now_date = datetime.datetime.now()
                if now_date >= validity_date:
                    continue;
            dumpedVoucher = json.loads(json.dumps(voucher, cls = AlchemyEncoder))
            vouchersJson.append({**dumpedVoucher, "credit": registeredVoucher.credit})

        return JSONResponse(content = vouchersJson, status_code = 200)
