import os
import base64

from urllib.error import HTTPError
from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.postgres_db import get_db

from schemas.User import UserSchema
from schemas.Invoice import InvoiceCustomSchema
from middleware.auth_guard import admin_required

from utils.common import is_false, is_not_empty
from utils.flag import is_flag_disabled, is_flag_enabled
from utils.date import parse_date
from utils.invoice import get_invoice_ref
from utils.logger import log_msg
from utils.mail import send_invoice_email
from utils.invoice import generate_invoice_pdf
from utils.payment import get_min_amount

router = APIRouter()

@router.post("")
def create_custom_invoice(current_user: Annotated[UserSchema, Depends(admin_required)], payload: InvoiceCustomSchema, db: Session = Depends(get_db)):
    email = payload.email
    send = payload.send
    preview = payload.preview
    items = payload.items
    fdate = parse_date(payload.date)
    invoice_date = fdate["value"]
    if is_false(fdate["status"]):
        return JSONResponse(content = {"error": "The date is not correct :{}".format(invoice_date), "i18n_code": "bad_date_aaaammdd"}, status_code = 400)

    from entities.User import User
    target_user = User.getUserByEmail(email, db)
    if not target_user:
        return JSONResponse(content = {"error": "user not found", "i18n_code": "304"}, status_code = 404)

    if is_flag_disabled(target_user.enabled_features, 'billable'):
        return JSONResponse(content = {"error": "user not billable", "i18n_code": "not_billable"}, status_code = 400)

    items_dict = []
    total_ht = 0
    for item in items:
        try:
            itemd = {
                "label": item.label,
                "price": item.price
            }
        except AttributeError as ae:
            return JSONResponse(content = {"error": "not correct item :{}".format(ae), "i18n_code": "not_correct_item"}, status_code = 400)

        total_ht = total_ht + itemd["price"]
        items_dict.append(itemd)

    total_ttc = 0
    timbre_fiscal = os.getenv("TIMBRE_FISCAL")
    if is_flag_disabled(target_user.enabled_features, 'without_vat'):
        total_ttc = round(total_ht, 4)
    elif is_not_empty(timbre_fiscal):
        total_ttc = round((total_ht * float(os.getenv("TTVA"))) + float(timbre_fiscal), 4)
    else:
        total_ttc = round(total_ht * float(os.getenv("TTVA")), 4)

    total_ht = round(total_ht, 4)
    from entities.Invoice import Invoice

    invoice_ref = get_invoice_ref(db)
    new_invoice = Invoice()
    new_invoice.ref = invoice_ref
    new_invoice.from_date = invoice_date
    new_invoice.to_date = invoice_date
    new_invoice.user_id = target_user.id
    new_invoice.total_price = total_ttc
    name_file = generate_invoice_pdf(invoice_ref, target_user, [], items_dict, invoice_date, invoice_date, total_ht, total_ttc, is_flag_enabled(target_user.enabled_features, 'without_vat'))
    min_amount = get_min_amount()

    try:
        encoded_string = ""
        with open(name_file, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()
        pdf_file.close()
        if is_false(preview):
            if total_ttc <= min_amount:
                new_invoice.status = "paid"

            new_invoice.save(db)

            if total_ttc > min_amount and is_flag_disabled(target_user.enabled_features, 'disable_emails'):
                send_invoice_email(email, name_file, encoded_string, send)

            log_msg("INFO", f"[api_invoice] Created new invoice for {invoice_date} for user {target_user.email}")

        os.remove(name_file)
    except HTTPError as e:
        return JSONResponse(content = {"error": e.msg, "i18n_code": e.headers["i18n_code"]}, status_code = e.code)
    return JSONResponse(content = {"file_name": name_file, "blob": str(encoded_string)}, status_code = 200)
