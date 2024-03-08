import json

from urllib.error import HTTPError
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from schemas.User import UserSchema
from schemas.Payment import PaymentSchema
from database.postgres_db import get_db
from middleware.auth_guard import admin_required

from utils.encoder import AlchemyEncoder
from utils import payment
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-payment"

@router.post("/{user_email}")
def pay(current_user: Annotated[UserSchema, Depends(admin_required)], user_email: str, payload: PaymentSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        invoice_id = payload.invoice_id
        voucher_id = payload.voucher_id

        if payment.PAYMENT_ADAPTER().is_disabled():
            return JSONResponse(content = {"message": "no payment enabled"}, status_code = 200)

        from entities.User import User
        user = User.getUserByEmail(user_email, db)
        if not user:
            return JSONResponse(content = {"error": "user not found"}, status_code = 404)

        from entities.Invoice import Invoice
        invoice = Invoice.getInvoiceById(invoice_id, db)
        if not invoice:
            return JSONResponse(content = {"error": "invoice not found", "i18n_code": "604"}, status_code = 404)

        if invoice.status == "paid":
            return JSONResponse(content = {"error": "invoice already paid", "i18n_code": "605"}, status_code = 404)
        try:
            user_json = json.loads(json.dumps(user, cls = AlchemyEncoder))
            return payment.pay(user = user_json, invoice = invoice, voucher_id = voucher_id, auto_pay = True, db = db)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
