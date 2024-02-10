from urllib.error import HTTPError
from utils.encoder import AlchemyEncoder
from utils import payment
import json
from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from schemas.Payment import PaymentSchema
from middleware.auth_guard import get_current_active_user
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("")
def pay(current_user: Annotated[UserSchema, Depends(get_current_active_user)], payload: PaymentSchema, db: Session = Depends(get_db)):
    invoice_id = payload.invoice_id
    voucher_id = payload.voucher_id

    if payment.PAYMENT_ADAPTER().is_disabled():
        return JSONResponse(content = {"message": "no payment enabled"}, status_code = 200)

    from entities.Invoice import Invoice
    from entities.User import User
    user = User.getUserById(current_user.id, db)
    invoice = Invoice.getInvoiceByIdAndUser(invoice_id, current_user.id, db)
    if not invoice:
        invoice = Invoice.getInvoiceByRefAndUser(invoice_id, current_user.id, db)

    if not invoice:
        return JSONResponse(content = {"error": "invoice not found", "i18n_code": "604"}, status_code = 404)

    if invoice.status == "paid":
        return JSONResponse(content = {"error": "invoice already paid", "i18n_code": "604"}, status_code = 404)

    try:
        user_json = json.loads(json.dumps(user, cls = AlchemyEncoder))
        return payment.pay(db, user_json, invoice, voucher_id)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
