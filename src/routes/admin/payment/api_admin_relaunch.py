import json

from urllib.error import HTTPError
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from database.postgres_db import get_db
from middleware.auth_guard import admin_required
from schemas.User import UserSchema
from schemas.Payment import PaymentRelaunchSchema

from utils.encoder import AlchemyEncoder
from utils.payment import relaunch
from utils.observability.otel import get_otel_tracer

router = APIRouter()

_span_prefix = "adm-payment-relaunch"

@router.post("/{user_email}")
def relaunch_payment(current_user: Annotated[UserSchema, Depends(admin_required)], user_email: str, payload: PaymentRelaunchSchema, db: Session = Depends(get_db)):
    with get_otel_tracer().start_as_current_span("{}-post".format(_span_prefix)):
        invoice_id = payload.invoice_id

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
            return relaunch(user = user_json, invoice = invoice)
        except HTTPError as e:
            return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
