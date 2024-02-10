from utils.encoder import AlchemyEncoder
from urllib.error import HTTPError
import json
from utils.payment import relaunch
from fastapi import Depends, APIRouter
from database.postgres_db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from schemas.User import UserSchema
from schemas.Payment import PaymentRelaunchSchema
from middleware.auth_guard import admin_required
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/{user_email}")
def relaunch(current_user: Annotated[UserSchema, Depends(admin_required)], user_email: str, payload: PaymentRelaunchSchema, db: Session = Depends(get_db)):
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
